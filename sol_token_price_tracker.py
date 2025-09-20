#!/usr/bin/env python3
"""
Solana代币价格追踪器
获取Solana上指定代币的价格，计算SOL兑代币的比值，并记录到本地文件
"""

import requests
import json
import datetime
import csv
import os
from typing import Dict, Optional, Tuple
import argparse
from dotenv import load_dotenv


class SolTokenPriceTracker:
    def __init__(self):
        # 加载.env文件
        load_dotenv()
        
        self.base_url = "https://api.coingecko.com/api/v3"
        self.sol_price_url = f"{self.base_url}/simple/price?ids=solana&vs_currencies=usd"
        self.data_file = "token_price_history.csv"
        
        # 从.env文件获取默认代币地址
        self.default_token_address = os.getenv('DEFAULT_TOKEN_ADDRESS')
        
        # 初始化CSV文件
        self._init_csv_file()
    
    def _init_csv_file(self):
        """初始化CSV文件，如果不存在则创建表头"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    '时间戳', '代币地址', '代币名称', '代币符号', 
                    'SOL价格(USD)', '代币价格(USD)', 'SOL/代币比值', 
                    '代币/SOL比值', '备注'
                ])
    
    def get_sol_price(self) -> Optional[float]:
        """获取SOL当前价格(USD)"""
        try:
            response = requests.get(self.sol_price_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['solana']['usd']
        except Exception as e:
            print(f"获取SOL价格失败: {e}")
            return None
    
    def get_token_info_by_address(self, token_address: str) -> Optional[Dict]:
        """通过代币地址获取代币信息"""
        try:
            # 使用CoinGecko的coins/list接口查找代币
            search_url = f"{self.base_url}/coins/list?include_platform=true"
            response = requests.get(search_url, timeout=15)
            response.raise_for_status()
            coins = response.json()
            
            # 查找匹配的Solana代币
            for coin in coins:
                if 'platforms' in coin and coin['platforms']:
                    solana_address = coin['platforms'].get('solana')
                    if solana_address and solana_address.lower() == token_address.lower():
                        return {
                            'id': coin['id'],
                            'name': coin['name'],
                            'symbol': coin['symbol']
                        }
            
            print(f"未找到地址为 {token_address} 的代币信息")
            return None
            
        except Exception as e:
            print(f"获取代币信息失败: {e}")
            return None
    
    def get_token_price(self, coin_id: str) -> Optional[float]:
        """通过coin ID获取代币价格"""
        try:
            price_url = f"{self.base_url}/simple/price?ids={coin_id}&vs_currencies=usd"
            response = requests.get(price_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[coin_id]['usd']
        except Exception as e:
            print(f"获取代币价格失败: {e}")
            return None
    
    def calculate_exchange_rates(self, sol_price: float, token_price: float) -> Tuple[float, float]:
        """计算SOL和代币之间的兑换比率"""
        sol_to_token = sol_price / token_price  # 1 SOL = ? Token
        token_to_sol = token_price / sol_price  # 1 Token = ? SOL
        return sol_to_token, token_to_sol
    
    def save_to_file(self, token_address: str, token_info: Dict, 
                     sol_price: float, token_price: float, 
                     sol_to_token: float, token_to_sol: float):
        """保存数据到CSV文件"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.data_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                token_address,
                token_info['name'],
                token_info['symbol'].upper(),
                f"{sol_price:.6f}",
                f"{token_price:.8f}",
                f"{sol_to_token:.8f}",
                f"{token_to_sol:.8f}",
                "自动记录"
            ])
    
    def track_token_price(self, token_address: str) -> bool:
        """主要功能：追踪指定代币价格并记录"""
        print(f"正在处理代币地址: {token_address}")
        
        # 1. 获取SOL价格
        print("获取SOL价格...")
        sol_price = self.get_sol_price()
        if not sol_price:
            print("无法获取SOL价格，退出")
            return False
        print(f"SOL当前价格: ${sol_price:.6f}")
        
        # 2. 获取代币信息
        print("获取代币信息...")
        token_info = self.get_token_info_by_address(token_address)
        if not token_info:
            print("无法获取代币信息，退出")
            return False
        print(f"代币信息: {token_info['name']} ({token_info['symbol'].upper()})")
        
        # 3. 获取代币价格
        print("获取代币价格...")
        token_price = self.get_token_price(token_info['id'])
        if not token_price:
            print("无法获取代币价格，退出")
            return False
        print(f"代币当前价格: ${token_price:.8f}")
        
        # 4. 计算兑换比率
        sol_to_token, token_to_sol = self.calculate_exchange_rates(sol_price, token_price)
        
        print("\n=== 兑换比率 ===")
        print(f"1 SOL = {sol_to_token:.8f} {token_info['symbol'].upper()}")
        print(f"1 {token_info['symbol'].upper()} = {token_to_sol:.8f} SOL")
        
        # 5. 保存到文件
        self.save_to_file(token_address, token_info, sol_price, token_price, 
                         sol_to_token, token_to_sol)
        print(f"\n数据已保存到 {self.data_file}")
        
        return True
    
    def show_history(self, limit: int = 10):
        """显示历史记录"""
        if not os.path.exists(self.data_file):
            print("没有历史记录文件")
            return
        
        print(f"\n=== 最近 {limit} 条记录 ===")
        with open(self.data_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
            if len(rows) <= 1:
                print("没有历史记录")
                return
            
            # 显示表头
            print("\t".join(rows[0]))
            print("-" * 100)
            
            # 显示最近的记录
            for row in rows[-limit:]:
                if row != rows[0]:  # 跳过表头
                    print("\t".join(row))


def main():
    parser = argparse.ArgumentParser(description='Solana代币价格追踪器')
    parser.add_argument('token_address', nargs='?', help='Solana代币地址（可选，不提供则使用.env中的DEFAULT_TOKEN_ADDRESS）')
    parser.add_argument('--history', '--hist', type=int, default=0, 
                       help='显示历史记录（指定条数）')
    
    args = parser.parse_args()
    
    tracker = SolTokenPriceTracker()
    
    if args.history > 0:
        tracker.show_history(args.history)
        return
    
    # 确定要使用的代币地址
    token_address = args.token_address
    if not token_address:
        token_address = tracker.default_token_address
        if not token_address:
            print("❌ 错误：没有提供代币地址，且.env文件中也没有设置DEFAULT_TOKEN_ADDRESS")
            print("请使用以下方式之一：")
            print("1. 直接提供代币地址：python sol_token_price_tracker.py <代币地址>")
            print("2. 在.env文件中设置DEFAULT_TOKEN_ADDRESS=<代币地址>")
            return
        else:
            print(f"使用.env文件中的默认代币地址: {token_address}")
    
    success = tracker.track_token_price(token_address)
    if success:
        print("\n✅ 价格追踪完成！")
    else:
        print("\n❌ 价格追踪失败！")


if __name__ == "__main__":
    main()

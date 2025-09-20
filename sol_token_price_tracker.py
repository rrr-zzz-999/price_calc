#!/usr/bin/env python3
"""
Solana代币价格追踪器 - 多API源版本
支持多个API源：CoinGecko, Jupiter, Solscan, Birdeye
获取Solana上指定代币的价格，计算SOL兑代币的比值，并记录到本地文件
"""

import requests
import json
import datetime
import csv
import os
import time
from typing import Dict, Optional, Tuple, List
import argparse
from dotenv import load_dotenv


class MultiApiSolTokenTracker:
    def __init__(self):
        # 加载.env文件
        load_dotenv()
        
        # 多API源配置
        self.api_sources = {
            'coingecko': {
                'name': 'CoinGecko',
                'base_url': 'https://api.coingecko.com/api/v3',
                'headers': {},
                'sol_mint': 'solana',
                'rate_limit': 10  # 每分钟请求数
            },
            'jupiter': {
                'name': 'Jupiter',
                'base_url': 'https://price.jup.ag',
                'headers': {},
                'sol_mint': 'So11111111111111111111111111111111111111112',
                'rate_limit': 100
            },
            'solscan': {
                'name': 'Solscan',
                'base_url': 'https://api.solscan.io',
                'headers': {'User-Agent': 'Mozilla/5.0'},
                'sol_mint': 'So11111111111111111111111111111111111111112',
                'rate_limit': 20
            },
            'dexscreener': {
                'name': 'DexScreener',
                'base_url': 'https://api.dexscreener.com',
                'headers': {},
                'sol_mint': 'So11111111111111111111111111111111111111112',
                'rate_limit': 300
            }
        }
        
        self.data_file = "token_price_history.csv"
        
        # 从.env文件获取配置
        self.default_token_address = os.getenv('DEFAULT_TOKEN_ADDRESS')
        self.preferred_apis = os.getenv('PREFERRED_APIS', 'jupiter,dexscreener,coingecko,solscan').split(',')
        
        # 缓存机制
        self._cache = {}
        self._cache_expiry = {}
        self._cache_duration = 300  # 5分钟缓存
        
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
                    '代币/SOL比值', '数据源', '备注'
                ])
    
    def _make_request(self, url: str, headers: dict = None, timeout: int = 10) -> Optional[requests.Response]:
        """发送HTTP请求"""
        try:
            response = requests.get(url, headers=headers or {}, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"请求失败 {url}: {e}")
            return None
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        return key in self._cache_expiry and time.time() < self._cache_expiry[key]
    
    def _set_cache(self, key: str, value):
        """设置缓存"""
        self._cache[key] = value
        self._cache_expiry[key] = time.time() + self._cache_duration
    
    def _get_cache(self, key: str):
        """获取缓存"""
        if self._is_cache_valid(key):
            return self._cache[key]
        return None
    
    def get_sol_price_jupiter(self) -> Optional[float]:
        """通过Jupiter API获取SOL价格"""
        try:
            sol_mint = self.api_sources['jupiter']['sol_mint']
            url = f"{self.api_sources['jupiter']['base_url']}/v4/price?ids={sol_mint}"
            
            response = self._make_request(url, self.api_sources['jupiter']['headers'])
            if not response:
                return None
            
            data = response.json()
            if 'data' in data and sol_mint in data['data']:
                return float(data['data'][sol_mint]['price'])
            return None
        except Exception as e:
            print(f"Jupiter API获取SOL价格失败: {e}")
            return None
    
    def get_sol_price_dexscreener(self) -> Optional[float]:
        """通过DexScreener API获取SOL价格"""
        try:
            sol_mint = self.api_sources['dexscreener']['sol_mint']
            url = f"{self.api_sources['dexscreener']['base_url']}/latest/dex/tokens/{sol_mint}"
            
            response = self._make_request(url, self.api_sources['dexscreener']['headers'])
            if not response:
                return None
            
            data = response.json()
            if 'pairs' in data and len(data['pairs']) > 0:
                # 取第一个交易对的价格
                return float(data['pairs'][0]['priceUsd'])
            return None
        except Exception as e:
            print(f"DexScreener API获取SOL价格失败: {e}")
            return None
    
    def get_sol_price_coingecko(self) -> Optional[float]:
        """通过CoinGecko API获取SOL价格"""
        try:
            url = f"{self.api_sources['coingecko']['base_url']}/simple/price?ids=solana&vs_currencies=usd"
            
            response = self._make_request(url, self.api_sources['coingecko']['headers'])
            if not response:
                return None
            
            data = response.json()
            if 'solana' in data and 'usd' in data['solana']:
                return float(data['solana']['usd'])
            return None
        except Exception as e:
            print(f"CoinGecko API获取SOL价格失败: {e}")
            return None
    
    def get_token_price_jupiter(self, token_address: str) -> Optional[Dict]:
        """通过Jupiter API获取代币价格"""
        try:
            url = f"{self.api_sources['jupiter']['base_url']}/v4/price?ids={token_address}"
            
            response = self._make_request(url, self.api_sources['jupiter']['headers'])
            if not response:
                return None
            
            data = response.json()
            if 'data' in data and token_address in data['data']:
                token_data = data['data'][token_address]
                return {
                    'price': float(token_data['price']),
                    'name': token_data.get('symbol', 'Unknown'),
                    'symbol': token_data.get('symbol', 'UNK'),
                    'source': 'Jupiter'
                }
            return None
        except Exception as e:
            print(f"Jupiter API获取代币价格失败: {e}")
            return None
    
    def get_token_price_dexscreener(self, token_address: str) -> Optional[Dict]:
        """通过DexScreener API获取代币价格"""
        try:
            url = f"{self.api_sources['dexscreener']['base_url']}/latest/dex/tokens/{token_address}"
            
            response = self._make_request(url, self.api_sources['dexscreener']['headers'])
            if not response:
                return None
            
            data = response.json()
            if 'pairs' in data and len(data['pairs']) > 0:
                # 选择流动性最高的交易对
                best_pair = max(data['pairs'], key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
                
                return {
                    'price': float(best_pair['priceUsd']),
                    'name': best_pair['baseToken']['name'],
                    'symbol': best_pair['baseToken']['symbol'],
                    'source': 'DexScreener'
                }
            return None
        except Exception as e:
            print(f"DexScreener API获取代币价格失败: {e}")
            return None
    
    def get_token_info_coingecko(self, token_address: str) -> Optional[Dict]:
        """通过CoinGecko API获取代币信息"""
        try:
            # 先尝试从缓存获取完整的代币列表
            cache_key = "coingecko_token_list"
            coins = self._get_cache(cache_key)
            
            if not coins:
                url = f"{self.api_sources['coingecko']['base_url']}/coins/list?include_platform=true"
                response = self._make_request(url, self.api_sources['coingecko']['headers'], timeout=20)
                if not response:
                    return None
                
                coins = response.json()
                self._set_cache(cache_key, coins)
                print("✅ 获取CoinGecko代币列表并缓存")
            else:
                print("📦 使用缓存的CoinGecko代币列表")
            
            # 查找匹配的Solana代币
            for coin in coins:
                if 'platforms' in coin and coin['platforms']:
                    solana_address = coin['platforms'].get('solana')
                    if solana_address and solana_address.lower() == token_address.lower():
                        # 获取价格
                        price_url = f"{self.api_sources['coingecko']['base_url']}/simple/price?ids={coin['id']}&vs_currencies=usd"
                        price_response = self._make_request(price_url, self.api_sources['coingecko']['headers'])
                        
                        if price_response:
                            price_data = price_response.json()
                            if coin['id'] in price_data:
                                return {
                                    'price': float(price_data[coin['id']]['usd']),
                                    'name': coin['name'],
                                    'symbol': coin['symbol'],
                                    'source': 'CoinGecko'
                                }
            return None
        except Exception as e:
            print(f"CoinGecko API获取代币信息失败: {e}")
            return None
    
    def get_multi_api_prices(self, token_address: str) -> Tuple[Optional[float], Optional[Dict], str]:
        """使用多个API源获取价格数据"""
        print("🌐 使用多API源获取价格数据...")
        
        sol_price = None
        token_info = None
        used_source = "未知"
        
        # 按优先级尝试不同的API源
        for api_name in self.preferred_apis:
            api_name = api_name.strip().lower()
            if api_name not in self.api_sources:
                continue
            
            print(f"🔄 尝试使用 {self.api_sources[api_name]['name']} API...")
            
            try:
                if api_name == 'jupiter':
                    if not sol_price:
                        sol_price = self.get_sol_price_jupiter()
                    if not token_info:
                        token_info = self.get_token_price_jupiter(token_address)
                
                elif api_name == 'dexscreener':
                    if not sol_price:
                        sol_price = self.get_sol_price_dexscreener()
                    if not token_info:
                        token_info = self.get_token_price_dexscreener(token_address)
                
                elif api_name == 'coingecko':
                    if not sol_price:
                        sol_price = self.get_sol_price_coingecko()
                    if not token_info:
                        token_info = self.get_token_info_coingecko(token_address)
                
                # 如果获取到了所需数据，记录数据源
                if sol_price and token_info:
                    used_source = self.api_sources[api_name]['name']
                    print(f"✅ 成功使用 {used_source} 获取价格数据")
                    break
                elif sol_price or token_info:
                    used_source = self.api_sources[api_name]['name']
                    print(f"⚠️ {used_source} 部分成功，继续尝试其他API...")
                
                # 添加延迟避免过快请求
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ {self.api_sources[api_name]['name']} API失败: {e}")
                continue
        
        return sol_price, token_info, used_source
    
    def calculate_exchange_rates(self, sol_price: float, token_price: float) -> Tuple[float, float]:
        """计算SOL和代币之间的兑换比率"""
        sol_to_token = sol_price / token_price  # 1 SOL = ? Token
        token_to_sol = token_price / sol_price  # 1 Token = ? SOL
        return sol_to_token, token_to_sol
    
    def save_to_file(self, token_address: str, token_info: Dict, 
                     sol_price: float, token_price: float, 
                     sol_to_token: float, token_to_sol: float, source: str):
        """保存数据到CSV文件"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.data_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                token_address,
                token_info.get('name', 'Unknown'),
                token_info.get('symbol', 'UNK').upper(),
                f"{sol_price:.6f}",
                f"{token_price:.8f}",
                f"{sol_to_token:.8f}",
                f"{token_to_sol:.8f}",
                source,
                "自动记录"
            ])
    
    def track_token_price(self, token_address: str) -> bool:
        """主要功能：追踪指定代币价格并记录"""
        print(f"🔍 正在处理代币地址: {token_address}")
        print(f"📋 API优先级: {' → '.join(self.preferred_apis)}")
        
        # 获取价格数据
        sol_price, token_info, source = self.get_multi_api_prices(token_address)
        
        if not sol_price:
            print("❌ 无法获取SOL价格")
            print("💡 建议：")
            print("   - 检查网络连接")
            print("   - 稍后重试（可能是API限制）")
            return False
        
        if not token_info:
            print("❌ 无法获取代币信息")
            print("💡 建议：")
            print("   - 确认代币地址是否正确")
            print("   - 该代币可能未在主要DEX上交易")
            return False
        
        token_price = token_info['price']
        
        print(f"✅ SOL当前价格: ${sol_price:.6f}")
        print(f"✅ 代币信息: {token_info['name']} ({token_info['symbol'].upper()})")
        print(f"✅ 代币当前价格: ${token_price:.8f}")
        print(f"📊 数据源: {source}")
        
        # 计算兑换比率
        sol_to_token, token_to_sol = self.calculate_exchange_rates(sol_price, token_price)
        
        print("\n" + "="*50)
        print("📈 兑换比率")
        print("="*50)
        print(f"1 SOL = {sol_to_token:,.8f} {token_info['symbol'].upper()}")
        print(f"1 {token_info['symbol'].upper()} = {token_to_sol:.8f} SOL")
        print("="*50)
        
        # 保存到文件
        self.save_to_file(token_address, token_info, sol_price, token_price, 
                         sol_to_token, token_to_sol, source)
        print(f"💾 数据已保存到 {self.data_file}")
        
        return True
    
    def show_history(self, limit: int = 10):
        """显示历史记录"""
        if not os.path.exists(self.data_file):
            print("❌ 没有历史记录文件")
            return
        
        print(f"\n📊 最近 {limit} 条记录")
        print("="*100)
        
        with open(self.data_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
            if len(rows) <= 1:
                print("📝 没有历史记录")
                return
            
            # 显示表头
            headers = rows[0]
            print(" | ".join(f"{h:^12}" for h in headers[:6]))
            print("-" * 100)
            
            # 显示最近的记录
            for row in rows[-limit:]:
                if row != rows[0]:  # 跳过表头
                    print(" | ".join(f"{cell:^12}" for cell in row[:6]))


def main():
    parser = argparse.ArgumentParser(description='Solana代币价格追踪器 - 多API源版本')
    parser.add_argument('token_address', nargs='?', 
                       help='Solana代币地址（可选，不提供则使用.env中的DEFAULT_TOKEN_ADDRESS）')
    parser.add_argument('--history', '--hist', type=int, default=0, 
                       help='显示历史记录（指定条数）')
    parser.add_argument('--apis', type=str,
                       help='指定使用的API源，逗号分隔（如：jupiter,dexscreener）')
    
    args = parser.parse_args()
    
    tracker = MultiApiSolTokenTracker()
    
    # 如果指定了API源，覆盖默认设置
    if args.apis:
        tracker.preferred_apis = [api.strip().lower() for api in args.apis.split(',')]
        print(f"🎯 使用指定的API源: {args.apis}")
    
    if args.history > 0:
        tracker.show_history(args.history)
        return
    
    # 确定要使用的代币地址
    token_address = args.token_address
    if not token_address:
        token_address = tracker.default_token_address
        if not token_address:
            print("❌ 错误：没有提供代币地址，且.env文件中也没有设置DEFAULT_TOKEN_ADDRESS")
            print("\n💡 解决方案：")
            print("1. 直接提供代币地址：")
            print("   python sol_token_price_tracker_multi_api.py <代币地址>")
            print("\n2. 创建.env文件设置默认地址：")
            print("   cp env_example.txt .env")
            print("   然后编辑.env文件设置DEFAULT_TOKEN_ADDRESS")
            print("\n3. 查看帮助：")
            print("   python sol_token_price_tracker_multi_api.py --help")
            return
        else:
            print(f"🎯 使用.env文件中的默认代币地址: {token_address}")
    
    success = tracker.track_token_price(token_address)
    if success:
        print("\n🎉 价格追踪完成！")
        print("📝 你可以使用 --history 参数查看历史记录")
        print("🔧 你可以使用 --apis 参数指定API源")
    else:
        print("\n❌ 价格追踪失败！")
        print("💡 尝试使用不同的API源：--apis jupiter,dexscreener")


if __name__ == "__main__":
    main()

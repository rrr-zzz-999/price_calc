#!/usr/bin/env python3
"""
使用示例：演示如何使用SolTokenPriceTracker类
"""

from sol_token_price_tracker import SolTokenPriceTracker

def main():
    # 创建追踪器实例
    tracker = SolTokenPriceTracker()
    
    # 一些常见的Solana代币地址用于测试
    test_tokens = {
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        # 你可以添加更多代币地址进行测试
    }
    
    print("=== Solana代币价格追踪器示例 ===\n")
    
    for token_name, token_address in test_tokens.items():
        print(f"正在测试 {token_name}...")
        success = tracker.track_token_price(token_address)
        if success:
            print(f"✅ {token_name} 价格获取成功\n")
        else:
            print(f"❌ {token_name} 价格获取失败\n")
        print("-" * 50)
    
    # 显示历史记录
    print("\n显示历史记录:")
    tracker.show_history(5)

if __name__ == "__main__":
    main()

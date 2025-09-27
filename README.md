# Solana代币价格追踪器

这个程序可以帮你获取Solana上任意代币的价格，计算SOL与该代币的兑换比值，以及计算SOL代币与以太坊代币的价格比值，并将结果记录到本地CSV文件中。

## 功能特性

- 🔍 通过代币地址自动获取代币信息（支持Solana和以太坊）
- 💰 实时获取SOL和目标代币的USD价格
- 📊 计算双向兑换比率（SOL→代币 和 代币→SOL）
- 🔄 **新功能：SOL代币与ETH代币价格比值计算**
- 📝 自动保存历史记录到CSV文件
- 📈 查看历史价格记录和比值计算记录
- 🌐 多API源支持（Jupiter、DexScreener、CoinGecko、1inch等）
- 🔄 智能重试机制处理API频率限制
- 💾 内存缓存减少重复请求
- 🎨 友好的用户界面和错误提示

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置默认代币地址

为了方便使用，你可以设置一个默认的代币地址，这样就不需要每次都输入代币地址了。

1. 复制 `env_example.txt` 文件并重命名为 `.env`
2. 在 `.env` 文件中设置你的默认代币地址：

```bash
# 创建配置文件
cp env_example.txt .env
```

编辑 `.env` 文件内容：
```
DEFAULT_TOKEN_ADDRESS=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

## 使用方法

### 基本用法

```bash
# 1. SOL代币价格追踪
python sol_token_price_tracker.py <SOL代币地址>

# 2. SOL代币与ETH代币价格比值计算
python sol_token_price_tracker.py <SOL代币地址> --eth-token <ETH代币地址>

# 3. 使用.env文件中配置的默认地址
python sol_token_price_tracker.py
```

### 示例

```bash
# 使用默认代币地址进行价格追踪
python sol_token_price_tracker.py

# 查询USDC价格
python sol_token_price_tracker.py EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

# 比较SOL代币与ETH USDC的价格比值
python sol_token_price_tracker.py J2bUGZDxRDpsVfjZqKwn6yYCUKFmqzHgt8UajhGtpump --eth-token 0xA0b86a33E6411e639c7a59ba0e5C3A0e2eE8cE0A

# 使用.env中的默认ETH代币地址进行比值计算
python sol_token_price_tracker.py J2bUGZDxRDpsVfjZqKwn6yYCUKFmqzHgt8UajhGtpump

# 指定API源
python sol_token_price_tracker.py <代币地址> --apis jupiter,dexscreener

# 运行示例程序
python comparison_example.py
```

### 查看历史记录

```bash
# 查看SOL代币价格历史记录
python sol_token_price_tracker.py --history 10

# 查看价格比值计算历史记录
python sol_token_price_tracker.py --comparison-history 10
```

## 配置文件说明

程序支持使用 `.env` 文件来配置默认设置：

### .env 文件格式
```
# SOL代币配置
DEFAULT_TOKEN_ADDRESS=你的默认SOL代币地址

# ETH代币配置（用于价格比值计算）
DEFAULT_ETH_TOKEN_ADDRESS=你的默认ETH代币地址

# API源配置
PREFERRED_APIS=jupiter,dexscreener,coingecko
```

### 使用优先级
**SOL代币地址：**
1. 命令行直接提供的代币地址（优先级最高）
2. .env文件中的DEFAULT_TOKEN_ADDRESS
3. 如果都没有提供，程序会显示错误提示

**ETH代币地址：**
1. 命令行 `--eth-token` 参数（优先级最高）
2. .env文件中的DEFAULT_ETH_TOKEN_ADDRESS
3. 如果都没有提供，只执行SOL代币价格追踪

## 输出示例

### SOL代币价格追踪示例
```
🔍 正在处理代币地址: J2bUGZDxRDpsVfjZqKwn6yYCUKFmqzHgt8UajhGtpump
📋 API优先级: dexscreener → coingecko → jupiter
🌐 使用多API源获取价格数据...
🔄 尝试使用 DexScreener API...
✅ 成功使用 DexScreener 获取价格数据
✅ SOL当前价格: $203.210000
✅ 代币信息: ∅ (∅)
✅ 代币当前价格: $0.00068430
📊 数据源: DexScreener

==================================================
📈 兑换比率
==================================================
1 SOL = 296,960.39748648 ∅
1 ∅ = 0.00000337 SOL
==================================================
💾 数据已保存到 token_price_history.csv

🎉 价格追踪完成！
```

### SOL与ETH代币比值计算示例
```
🔍 正在比较代币价格:
   SOL代币: J2bUGZDxRDpsVfjZqKwn6yYCUKFmqzHgt8UajhGtpump
   ETH代币: 0xA0b86a33E6411e639c7a59ba0e5C3A0e2eE8cE0A
============================================================

📊 获取SOL代币价格...
✅ 成功使用 DexScreener 获取价格数据

📊 获取ETH代币价格...
✅ 成功使用 CoinGecko 获取以太坊代币价格

============================================================
💰 获取到的价格信息
============================================================
SOL代币: ∅ (∅)
  价格: $0.00068430
  数据源: DexScreener

ETH代币: USD Coin (USDC)
  价格: $1.00000000
  数据源: CoinGecko

============================================================
📈 代币价格比值分析
============================================================
1 ∅ = 0.00068430 USDC
1 USDC = 1461.42857143 ∅

💡 USDC 比 ∅ 贵 1461.43 倍
============================================================
💾 比较结果已保存到 token_price_comparison.csv

🎉 代币比值计算完成！
```

## 数据文件

程序会创建两个CSV文件：

### 1. `token_price_history.csv` - SOL代币价格历史
- 时间戳
- 代币地址
- 代币名称
- 代币符号
- SOL价格(USD)
- 代币价格(USD)
- SOL/代币比值
- 代币/SOL比值
- 数据源
- 备注

### 2. `token_price_comparison.csv` - 代币价格比值计算历史
- 时间戳
- SOL代币地址、名称、符号、价格
- ETH代币地址、名称、符号、价格
- SOL代币/ETH代币比值
- ETH代币/SOL代币比值
- 数据源信息

## 注意事项

1. **代币地址格式**：
   - SOL代币：请确保使用正确的Solana代币地址（Base58格式）
   - ETH代币：请确保使用正确的以太坊代币地址（0x开头的十六进制格式）

2. **网络连接**：程序需要互联网连接来获取价格数据

3. **API限制**：程序使用多个API源，内置智能切换机制
   - 程序内置智能重试机制，遇到限制会自动等待重试
   - 内存缓存机制减少重复请求
   - 如果连续失败，请等待几分钟后重试

4. **代币支持**：
   - SOL代币：支持在Jupiter、DexScreener、CoinGecko上有记录的代币
   - ETH代币：支持在CoinGecko、1inch上有记录的代币

## 支持的API源

### Solana代币价格API：
- **Jupiter**: 快速，数据准确，适合实时交易数据
- **DexScreener**: 覆盖面广，流动性信息丰富
- **CoinGecko**: 稳定，但有请求频率限制
- **Solscan**: 官方数据，但API限制较多

### 以太坊代币价格API：
- **CoinGecko**: 覆盖面广，数据稳定
- **1inch**: 聚合器价格，反映真实交易价格

## 常见代币地址

### Solana代币：
- **USDC**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **USDT**: `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB`
- **RAY**: `4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R`

### 以太坊代币：
- **USDC**: `0xA0b86a33E6411e639c7a59ba0e5C3A0e2eE8cE0A`
- **USDT**: `0xdAC17F958D2ee523a2206206994597C13D831ec7`
- **UNI**: `0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984`
- **WETH**: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`

## 错误处理

如果遇到以下情况，程序会显示相应错误信息：
- 代币地址无效或未找到
- 网络连接问题
- API请求失败
- 价格数据获取失败

## 高级功能

### 命令行参数
- `--eth-token`: 指定以太坊代币地址进行比值计算
- `--history`: 查看SOL代币价格历史记录
- `--comparison-history`: 查看价格比值计算历史记录
- `--apis`: 指定使用的API源

### 配置文件支持
- 支持通过.env文件配置默认代币地址
- 支持配置API源优先级
- 支持配置默认ETH代币地址

## 技术实现

- 多API源支持：Jupiter、DexScreener、CoinGecko、1inch
- 智能API切换和重试机制
- 内存缓存优化性能
- CSV格式保存历史数据
- 完整的命令行参数处理

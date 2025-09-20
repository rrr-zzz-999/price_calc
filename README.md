# Solana代币价格追踪器

这个程序可以帮你获取Solana上任意代币的价格，计算SOL与该代币的兑换比值，并将结果记录到本地CSV文件中。

## 功能特性

- 🔍 通过代币地址自动获取代币信息
- 💰 实时获取SOL和目标代币的USD价格
- 📊 计算双向兑换比率（SOL→代币 和 代币→SOL）
- 📝 自动保存历史记录到CSV文件
- 📈 查看历史价格记录
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
# 使用指定的代币地址
python sol_token_price_tracker.py <代币地址>

# 使用.env文件中配置的默认代币地址
python sol_token_price_tracker.py
```

### 示例

```bash
# 使用默认代币地址（需要先配置.env文件）
python sol_token_price_tracker.py

# 查询USDC价格（示例地址）
python sol_token_price_tracker.py EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

# 查询其他代币价格
python sol_token_price_tracker.py YOUR_TOKEN_ADDRESS_HERE
```

### 查看历史记录

```bash
# 查看最近10条记录
python sol_token_price_tracker.py --history 10

# 查看最近5条记录（使用简写）
python sol_token_price_tracker.py --hist 5
```

## 配置文件说明

程序支持使用 `.env` 文件来配置默认设置：

### .env 文件格式
```
DEFAULT_TOKEN_ADDRESS=你的默认代币地址
```

### 使用优先级
1. 命令行直接提供的代币地址（优先级最高）
2. .env文件中的DEFAULT_TOKEN_ADDRESS
3. 如果都没有提供，程序会显示错误提示

## 输出示例

```
正在处理代币地址: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
获取SOL价格...
SOL当前价格: $142.350000
获取代币信息...
代币信息: USD Coin (USDC)
获取代币价格...
代币当前价格: $1.00000000

=== 兑换比率 ===
1 SOL = 142.35000000 USDC
1 USDC = 0.00702459 SOL

数据已保存到 token_price_history.csv

✅ 价格追踪完成！
```

## 数据文件

程序会在当前目录创建 `token_price_history.csv` 文件，包含以下字段：

- 时间戳
- 代币地址
- 代币名称
- 代币符号
- SOL价格(USD)
- 代币价格(USD)
- SOL/代币比值
- 代币/SOL比值
- 备注

## 注意事项

1. **代币地址格式**：请确保使用正确的Solana代币地址（Base58格式）
2. **网络连接**：程序需要互联网连接来获取价格数据
3. **API限制**：使用CoinGecko免费API，有请求频率限制
   - 程序内置智能重试机制，遇到限制会自动等待重试
   - 内存缓存机制减少重复请求
   - 如果连续失败，请等待几分钟后重试
4. **代币支持**：只支持在CoinGecko上有记录的Solana代币

## 常见Solana代币地址

- **USDC**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **USDT**: `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB`
- **RAY**: `4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R`

## 错误处理

如果遇到以下情况，程序会显示相应错误信息：
- 代币地址无效或未找到
- 网络连接问题
- API请求失败
- 价格数据获取失败

## 技术实现

- 使用CoinGecko API获取价格数据
- 通过代币地址匹配获取代币信息
- CSV格式保存历史数据
- 支持命令行参数处理

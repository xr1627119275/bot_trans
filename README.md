# 🤖 Telegram 翻译机器人

中英文自动互译机器人

## 功能
- 中文 → 英文
- 英文 → 中文

## 命令
| 命令 | 说明 |
|------|------|
| `/on` | 开启翻译 |
| `/off` | 关闭翻译 |
| `/help` | 帮助信息 |

## 本地运行

```bash
pip install -r requirements.txt
```

**PowerShell:**
```powershell
$env:BOT_TOKEN="your_token"
python main.py
```

**CMD:**
```cmd
set BOT_TOKEN=your_token
python main.py
```

**Linux/Mac:**
```bash
export BOT_TOKEN="your_token"
python main.py
```

## 部署

设置环境变量 `BOT_TOKEN` 即可。

支持 Railway / Render / Koyeb 等平台。


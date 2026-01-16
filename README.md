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

### Railway / Render / Koyeb
设置环境变量 `BOT_TOKEN` 即可。

### Cloudflare Workers

```bash
cd cloudflare-worker
npm install -g wrangler
wrangler login
wrangler secret put BOT_TOKEN
wrangler deploy
```

部署后设置 Webhook：
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-worker.workers.dev
```


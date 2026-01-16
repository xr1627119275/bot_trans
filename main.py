"""
Telegram 翻译机器人
- 中文自动翻译成英文
- 英文自动翻译成中文
"""

import os
import re
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token (从环境变量读取)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ 请设置环境变量 BOT_TOKEN")

# 翻译API URL (使用免费的Google翻译API)
TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

# 存储每个聊天的翻译开关状态 {chat_id: True/False}
translate_enabled = {}


def contains_chinese(text: str) -> bool:
    """检测文本是否包含中文字符"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf\uf900-\ufaff\u2f800-\u2fa1f]')
    return bool(chinese_pattern.search(text))


def is_mostly_chinese(text: str) -> bool:
    """判断文本是否主要是中文"""
    if not text.strip():
        return False
    
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(re.findall(r'\w', text))
    
    if total_chars == 0:
        return contains_chinese(text)
    
    return chinese_chars / max(total_chars, 1) > 0.3


async def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """使用Google翻译API进行翻译"""
    import aiohttp
    
    params = {
        'client': 'gtx',
        'sl': source_lang,
        'tl': target_lang,
        'dt': 't',
        'q': text
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(TRANSLATE_URL, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    # 解析返回结果
                    translated_parts = []
                    if result and result[0]:
                        for part in result[0]:
                            if part[0]:
                                translated_parts.append(part[0])
                    return ''.join(translated_parts)
                else:
                    logger.error(f"翻译API返回错误: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"翻译出错: {e}")
        return None


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /help 命令"""
    help_text = """🤖 <b>翻译机器人帮助</b>

<b>📋 可用命令：</b>
/help - 显示此帮助信息
/on - 开启翻译功能
/off - 关闭翻译功能

<b>🔄 翻译规则：</b>
• 中文消息 → 自动翻译成英文
• 英文消息 → 自动翻译成中文

<b>📝 使用方法：</b>
1. 发送 /on 开启翻译
2. 直接发送文字即可自动翻译
3. 发送 /off 关闭翻译"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def start_translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /on 命令 - 开启翻译"""
    chat_id = update.effective_chat.id
    translate_enabled[chat_id] = True
    await update.message.reply_text("✅ 翻译功能已开启！\n\n发送任意文字即可自动翻译。")


async def stop_translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /off 命令 - 关闭翻译"""
    chat_id = update.effective_chat.id
    translate_enabled[chat_id] = False
    await update.message.reply_text("❌ 翻译功能已关闭。\n\n发送 /on 可重新开启。")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理所有文本消息并进行翻译"""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    
    # 检查翻译功能是否开启
    if not translate_enabled.get(chat_id, False):
        return
    
    text = update.message.text.strip()
    
    if not text:
        return
    
    # 判断语言并翻译
    if is_mostly_chinese(text):
        # 中文 -> 英文
        source_lang = 'zh-CN'
        target_lang = 'en'
    else:
        # 英文 -> 中文
        source_lang = 'en'
        target_lang = 'zh-CN'
    
    # 执行翻译
    translated = await translate_text(text, source_lang, target_lang)
    
    if translated:
        await update.message.reply_text(translated)
    else:
        await update.message.reply_text("❌ 翻译失败，请稍后重试")


def main() -> None:
    """启动机器人"""
    print("🤖 翻译机器人启动中...")
    
    # 创建应用
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("on", start_translate))
    application.add_handler(CommandHandler("off", stop_translate))
    
    # 添加消息处理器 - 处理所有文本消息
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ 机器人已启动！等待消息...")
    
    # 启动机器人
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

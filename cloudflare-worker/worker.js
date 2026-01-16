/**
 * Telegram 翻译机器人 - Cloudflare Workers 版本
 * 中文 ↔ 英文 自动互译
 */

// 从环境变量获取 Bot Token
const TRANSLATE_URL = 'https://translate.googleapis.com/translate_a/single';

// 存储翻译开关状态 (使用 KV 存储，这里用内存模拟)
const translateEnabled = new Map();

/**
 * 检测是否主要是中文
 */
function isMostlyChinese(text) {
  const chineseChars = (text.match(/[\u4e00-\u9fff]/g) || []).length;
  const totalChars = (text.match(/\w/g) || []).length;
  if (totalChars === 0) {
    return /[\u4e00-\u9fff]/.test(text);
  }
  return chineseChars / Math.max(totalChars, 1) > 0.3;
}

/**
 * 翻译文本
 */
async function translateText(text, sourceLang, targetLang) {
  const params = new URLSearchParams({
    client: 'gtx',
    sl: sourceLang,
    tl: targetLang,
    dt: 't',
    q: text
  });

  try {
    const response = await fetch(`${TRANSLATE_URL}?${params}`);
    if (response.ok) {
      const result = await response.json();
      if (result && result[0]) {
        return result[0].map(part => part[0] || '').join('');
      }
    }
  } catch (e) {
    console.error('翻译错误:', e);
  }
  return null;
}

/**
 * 发送 Telegram 消息
 */
async function sendMessage(botToken, chatId, text) {
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML' })
  });
}

/**
 * 处理 Telegram 更新
 */
async function handleUpdate(botToken, update) {
  const message = update.message;
  if (!message || !message.text) return;

  const chatId = message.chat.id;
  const text = message.text.trim();

  // 处理命令
  if (text === '/help') {
    const helpText = `🤖 <b>翻译机器人帮助</b>

<b>📋 可用命令：</b>
/help - 显示此帮助信息
/on - 开启翻译功能
/off - 关闭翻译功能

<b>🔄 翻译规则：</b>
• 中文消息 → 自动翻译成英文
• 英文消息 → 自动翻译成中文`;
    await sendMessage(botToken, chatId, helpText);
    return;
  }

  if (text === '/on') {
    translateEnabled.set(chatId, true);
    await sendMessage(botToken, chatId, '✅ 翻译功能已开启！');
    return;
  }

  if (text === '/off') {
    translateEnabled.set(chatId, false);
    await sendMessage(botToken, chatId, '❌ 翻译功能已关闭。');
    return;
  }

  // 检查翻译是否开启
  if (!translateEnabled.get(chatId)) return;

  // 翻译消息
  const sourceLang = isMostlyChinese(text) ? 'zh-CN' : 'en';
  const targetLang = isMostlyChinese(text) ? 'en' : 'zh-CN';

  const translated = await translateText(text, sourceLang, targetLang);
  if (translated) {
    await sendMessage(botToken, chatId, translated);
  } else {
    await sendMessage(botToken, chatId, '❌ 翻译失败，请稍后重试');
  }
}

/**
 * Worker 入口
 */
export default {
  async fetch(request, env) {
    const botToken = env.BOT_TOKEN;

    if (request.method === 'POST') {
      try {
        const update = await request.json();
        await handleUpdate(botToken, update);
      } catch (e) {
        console.error('处理更新错误:', e);
      }
    }

    return new Response('OK', { status: 200 });
  }
};


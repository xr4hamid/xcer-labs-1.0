const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  delay,
} = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const axios = require('axios');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
const P = require('pino');
const sendContactImage = require('./contact');
const allowGroupReplies = process.env.REPLY_IN_GROUPS === 'true';


const INTEREST_KEYWORDS = [
  "interested", "contact", "need service", "want automation", "xcer labs", "services"
];

// Configuration
const CONFIG = {
  AI_ENDPOINT: process.env.AI_ENDPOINT || 'http://127.0.0.1:5000/chat',
  SESSION_PATH: './auth_info',
  MAX_RETRIES: 5,
  RETRY_DELAY: 5000,
  ADMIN_NUMBERS: process.env.ADMIN_NUMBERS ? process.env.ADMIN_NUMBERS.split(',') : [],
  THROTTLE_DELAY: 1000,
};

// Functions

function isInterestedMessage(text) {
  const msg = text.toLowerCase();

const keywords = [
  "interested",
  "i want",
  "need bot",
  "need ai",
  "custom bot",
  "automation",
  "whatsapp bot",
  "xcer",
  "how much",
  "cost",
  "build a bot",
  "developer",
  "can you make",
  "tell me more",
  "services",
  "contact",
  "pricing",
  "quote",
  "rates",
  "support",
  "number",
  "phone",
];

  return keywords.some(keyword => msg.includes(keyword));
}




function log(message, level = 'info') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  console.log(logMessage);
  if (process.env.LOG_FILE) {
    fs.appendFileSync(process.env.LOG_FILE, logMessage + '\n');
  }
}

// Throttled message queue
const messageQueue = new Map();
async function processQueue(sock, jid) {
  if (messageQueue.has(jid) && messageQueue.get(jid).length > 0) {
    const { text } = messageQueue.get(jid).shift();
    try {
await sock.sendMessage(jid, {
  text: text.trim(), // removes extra spaces
});
      log(`Message sent to ${jid}`);
    } catch (error) {
      log(`Failed to send message to ${jid}: ${error.message}`, 'error');
      messageQueue.get(jid).unshift({ text });
    }

    if (messageQueue.get(jid).length > 0) {
      setTimeout(() => processQueue(sock, jid), CONFIG.THROTTLE_DELAY);
    }
  }
}

async function sendMessageWithThrottle(sock, jid, text) {
  if (!messageQueue.has(jid)) {
    messageQueue.set(jid, []);
  }
  messageQueue.get(jid).push({ text });

  if (messageQueue.get(jid).length === 1) {
    processQueue(sock, jid);
  }
}

// AI Response
async function getAIResponse(text, sender, retries = 0) {
  try {
    const aiRes = await axios.post(CONFIG.AI_ENDPOINT, {
  message: `You are chatting with a WhatsApp user. Reply in a friendly, casual, and human tone as a helpful assistant from XCER Labs. Keep it short, warm, and natural.\n\nUser: ${text}`,
      sender: sender,
    }, { timeout: 10000 });

    return aiRes.data.reply;
  } catch (err) {
    if (retries < CONFIG.MAX_RETRIES) {
      log(`AI request failed (attempt ${retries + 1}), retrying...`, 'warn');
      await delay(CONFIG.RETRY_DELAY);
      return getAIResponse(text, sender, retries + 1);
    }
    throw err;
  }
}

// Bot start
async function startBot(retryCount = 0) {
  try {
    log(`Initializing WhatsApp bot (attempt ${retryCount + 1})`);
    const { state, saveCreds } = await useMultiFileAuthState(CONFIG.SESSION_PATH);
    const { version } = await fetchLatestBaileysVersion();

    const sock = makeWASocket({
      version,
      auth: state,
      printQRInTerminal: false,
      logger: P({ level: 'silent' }),
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', ({ connection, lastDisconnect, qr }) => {
      if (qr) {
        log('Scan this QR to authenticate:');
        qrcode.generate(qr, { small: true });
      }

      if (connection === 'close') {
        const shouldReconnect = lastDisconnect?.error &&
          new Boom(lastDisconnect.error).output.statusCode !== DisconnectReason.loggedOut;

        if (shouldReconnect && retryCount < CONFIG.MAX_RETRIES) {
          log('Connection closed, retrying...');
          setTimeout(() => startBot(retryCount + 1), CONFIG.RETRY_DELAY);
        } else {
          log('Logged out. Delete auth_info folder to scan QR again.');
        }
      } else if (connection === 'open') {
        log('✅ Connected to WhatsApp!');
      }
    });

    // Main message handler Messageupsert
    sock.ev.on('messages.upsert', async ({ messages }) => {
    let sender = null;  // ✅ Declare here for use in catch
      try {
        const msg = messages[0];
        if (!msg.message || msg.key.fromMe) return;

        const sender = msg.key.remoteJid;
        // 🔐 Check for group and REPLY_IN_GROUPS setting
const isGroup = sender.endsWith('@g.us');
const allowGroupReplies = process.env.REPLY_IN_GROUPS === 'true';
if (isGroup && !allowGroupReplies) {
  log(`🚫 Ignored message from group: ${sender}`);
  return;
}
        const text = msg.message.conversation ||
                     msg.message.extendedTextMessage?.text ||
                     msg.message.imageMessage?.caption ||
                     '';

        log(`Message from ${sender}: ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`);

        // Check for interest msg intent
          const isInterestMessage = isInterestedMessage(text);


        if (isInterestMessage) {
          log(`Sending contact image to ${sender}`);
          await sendContactImage(sock, sender);
          return; // 🚫 Don't call Flask for this
        }

        // Admin commands
        if (CONFIG.ADMIN_NUMBERS.includes(sender.split('@')[0])) {
          if (text === '!status') {
            await sendMessageWithThrottle(sock, sender, '🤖 Bot is running normally');
            return;
          }
          if (text === '!restart') {
            await sendMessageWithThrottle(sock, sender, '🔄 Restarting bot...');
            process.exit(0);
          }
        }

        // All other messages → AI
        const reply = await getAIResponse(text, sender);
        await sendMessageWithThrottle(sock, sender, reply);

      } catch (error) {
        log(`Error processing message: ${error.message}`, 'error');
        await sendMessageWithThrottle(sock, sender,
          "Our bot is currently having a temporary issue. Please try again shortly!"
        );
      }
    });

    // Optional events
    sock.ev.on('messages.update', () => {});
    sock.ev.on('message-receipt.update', () => {});
    sock.ev.on('presence.update', () => {});

    // Cleanup
    process.on('SIGINT', () => {
      log('Shutting down...');
      sock.end();
      process.exit(0);
    });

  } catch (error) {
    log(`Initialization error: ${error.message}`, 'error');
    if (retryCount < CONFIG.MAX_RETRIES) {
      log(`Retrying in ${CONFIG.RETRY_DELAY / 1000} seconds...`);
      await delay(CONFIG.RETRY_DELAY);
      startBot(retryCount + 1);
    } else {
      log('Max initialization attempts reached.', 'error');
    }
  }
}

startBot();

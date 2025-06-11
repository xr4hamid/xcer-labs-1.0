const fs = require("fs");
const path = require("path");

module.exports = async function sendContact(sock, jid) {
  try {

    // Prepare and send the local image
    const imagePath = path.join(__dirname, "assets", "xcer.png");
    const imageBuffer = fs.readFileSync(imagePath);

    const caption = `🧠 *Need AI, Automation or a Custom WhatsApp Bot?*

Meet *Hamid – Founder of XCER Labs*, where we build: 
✅ AI tools, 🤖 smart bots, 🌐 eCommerce systems, and more!

📲 Message him directly on WhatsApp:`;

    await sock.sendMessage(jid, {
      image: imageBuffer,
      caption: caption,
    });
    const contactMessage = {
      contacts: {
        displayName: "XCER Labs",
        contacts: [
          {
            displayName: "XCER Labs",
            vcard: `
BEGIN:VCARD
VERSION:3.0
FN:XCER Labs
ORG:XCER Labs;
TEL;type=CELL;type=VOICE;waid=923137777404:+92 313 7777404
EMAIL:xcer.ai.team@gmail.com
URL:https://xcerlabs.com
END:VCARD`,
          },
        ],
      },
    };

    // Send contact card first
    await sock.sendMessage(jid, contactMessage);

    console.log(`[INFO] Sent contact and image to ${jid}`);
  } catch (err) {
    console.error(`[ERROR] Failed to send contact image: ${err.message}`);
  }
};

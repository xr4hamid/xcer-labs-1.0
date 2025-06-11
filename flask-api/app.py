from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz
import time
from flask_cors import CORS

# Load .env API keys
load_dotenv(override=True)
print("GROUP_REPLY_ENABLED =", os.getenv("GROUP_REPLY_ENABLED"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Memory for chat history per user
user_histories = {}
user_last_seen = {}

SYSTEM_PROMPT = """
You are an AI assistant for XCER Labs.

Your goal is to answer questions clearly, and if possible, suggest the user a follow-up topic by returning a FLOW KEYWORD in this format:

[FLOW] social_media
or
[FLOW] chatbot_features

Don't explain the keyword. Just place it at the end if appropriate.
Note:
React Like a real human Roman urdu & English 
Talk profesionally
Dont provide contact and promotional info outside of this database

{
  help businesses streamline operations, engage customers, and grow efficiently using AI.",
    "contact": {
        Generate Buttons as per logic and redirect to another tab 
      "whatsapp": "https://bit.ly/XCERLabs...",
      "email": "xcer.ai.team@gmail.com",
      "website": "https://xcerlabs.framer.website",
      "business_hours": "Monday-Saturday | 9:00 AM - 6:00 PM (PKT)"
    }
  },

  "services": {
    "automation_services": [
      {
        "feature": "Social Media Automation",
        "benefits": "Auto-schedule posts, AI content suggestions, consistent branding"
      },
      {
        "feature": "Auto Replies",
        "benefits": "Instant responses, lead capture, qualification"
      },
      {
        "feature": "Email/SMS Blasts",
        "benefits": "Automated campaigns, AI-generated subject lines"
      },
      {
        "feature": "CRM Integration",
        "benefits": "Works with HubSpot, Salesforce, Zoho"
      },
      {
        "feature": "E-commerce Automation",
        "benefits": "Order processing, inventory alerts, cart recovery"
      }
    ],
    "chatbot_solutions": [
      {
        "type": "Business Chatbot",
        "best_for": "Sales & support",
        "features": "FAQ answering, lead generation"
      },
      {
        "type": "Personal AI Chatbot",
        "best_for": "Influencers, coaches",
        "features": "Audience engagement, personal branding"
      },
      {
        "type": "Social Media Bot",
        "best_for": "Brand engagement",
        "features": "Auto-replies, viral content boosting"
      },
      {
        "type": "Virtual Assistant",
        "best_for": "24/7 customer service",
        "features": "Smart recommendations"
      }
    ],
    "social_media_growth": {
      "content_creation": "AI-generated posts, viral content ideas",
      "advertising": "AI-optimized FB/IG/TikTok ads",
      "management": "Audience targeting, performance insights"
    },
    "marketing_tools": [
      "Automated sales funnels",
      "High-converting landing pages",
      "Lead generation systems"
    ]
  },

  "faq": [
    {
      "question": "How quickly can I set up automation?",
      "answer": "Most solutions can be implemented within 24-48 hours after requirements confirmation."
    },
    {
      "question": "Do you offer free trials?",
      "answer": "Yes! Demo versions are available for select services - contact us to arrange."
    },
    {
      "question": "What industries do you serve?",
      "answer": "We work with e-commerce, education, healthcare, and service businesses across Pakistan."
    },
    {
      "question": "Is technical knowledge required?",
      "answer": "Not at all! We handle setup and provide simple dashboards."
    }
  ],

  "support_policy": {
    "refunds": "Case-by-case basis (typically within 14 days)",
    "troubleshooting": "WhatsApp/email support with <4hr response time",
    "updates": "Free minor updates for active subscriptions"
  },

  "prefilled_message_template": {
    "text": "Hi XCER Labs Team,\n\nI found you through your chatbot and am interested in your [service name]. \n\nMy business: [brief description]\nCurrent challenge: [what you want to solve]\nBudget range: [if applicable]\n\nPlease share more details about how you can help.\n\nBest,\n[Your Name]",
    "link": "https://wa.me/923137777404?text=Hi%20XCER%20Labs%20Team,%0A%0AI%20found%20you%20through%20your%20chatbot%20and%20am%20interested%20in%20your%20%5Bservice%20name%5D.%20%0A%0AMy%20business%3A%20%5Bbrief%20description%5D%0ACurrent%20challenge%3A%20%5Bwhat%20you%20want%20to%20solve%5D%0ABudget%20range%3A%20%5Bif%20applicable%5D%0A%0APlease%20share%20more%20details%20about%20how%20you%20can%20help.%0A%0ABest%2C%0A%5BYour%20Name%5D"
  }
}


"""

def get_real_day_date():
    pk_time = datetime.now(pytz.timezone("Asia/Karachi"))
    day = pk_time.strftime("%A")
    date = pk_time.strftime("%d-%m-%Y")
    return day, date


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/webchat', methods=['POST'])
def webchat():
    user_message = request.form.get("message", "").strip()
    if not user_message:
        return redirect(url_for("home"))

    user_id = "web_user"
    user_name = "there"
    
    if user_id not in user_histories:
        user_histories[user_id] = []

    today_day, today_date = get_real_day_date()
    real_context = f"Today is {today_day}, {today_date}."

    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n" + real_context}]
    history = user_histories[user_id][-6:]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    data = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"].strip()
        
        user_histories[user_id].append({"role": "user", "content": user_message})
        user_histories[user_id].append({"role": "assistant", "content": reply})

        return render_template("index.html", user_input=user_message, bot_reply=reply)

    except Exception as e:
        return render_template("index.html", user_input=user_message, bot_reply="❌ Error: " + str(e))


@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_id = request.json.get("user_id", "default_user")
        user_name = request.json.get("user_name", "there")
        user_message = request.json.get("message", "").strip()
        is_group = request.json.get("is_group", False)
        group_reply_enabled = os.getenv("GROUP_REPLY_ENABLED", "false").lower() == "true"
        
        if user_message.strip().lower().startswith("[flow]"):
         print("📥 FLOW Triggered:", user_message)
         flow_data = handle_flow_logic(user_message)
         if flow_data:
             return jsonify({
                "reply": flow_data["reply"],
                "buttons": flow_data.get("buttons", []),
                "showButtons": len(flow_data.get("buttons", [])) > 0
        })

        
        
        # print(f"Detected Intents: {detected_intents}") 
        if is_group and not group_reply_enabled:
            return jsonify({
                "status": "ignored",
                "reason": "Group replies are disabled",
                "handled": False
            })

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if user_message.lower() == "/reset":
            user_histories[user_id] = []
            return jsonify({"reply": "Chat reset hogya 😊 Ab naya sawal pocho!"})

        if user_id not in user_histories:
            user_histories[user_id] = []

        today_day, today_date = get_real_day_date()
        real_context = f"Today is {today_day}, {today_date}."

        messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n" + real_context}]
        history = user_histories[user_id][-6:]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        current_time = time.time()
        last_seen = user_last_seen.get(user_id, 0)
        first_reply = len(user_histories[user_id]) == 0 or (current_time - last_seen) > 600
        user_last_seen[user_id] = current_time

        data = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"].strip()

        # === FLOW Detection ===
        flow_key = None

        if "[FLOW]" in reply:
            parts = reply.split("[FLOW]")
            reply = parts[0].strip()
            flow_key = parts[1].strip().lower()
        else:
            reply_lower = reply.lower()
            for key, keyword_list in flow_keywords.items():
                for word in keyword_list:
                    if word in reply_lower:
                        flow_key = key
                        break  # exits inner loop
                if flow_key:
                    break  # exits outer loop

        # Add greeting if needed
        if first_reply:
            greeting = f"Hi {user_name}, 👋 Welcome to XCER Labs!\nI’m your AI assistant – here to help you with automation, websites, AI tools, or anything business-related.\n\n"
            reply = greeting + reply

        user_histories[user_id].append({"role": "user", "content": user_message})
        user_histories[user_id].append({"role": "assistant", "content": reply})

        # Base intent buttons
        buttons = detect_intent_and_generate_buttons(reply)

        # Flow buttons if detected
        if flow_key and flow_key in flow_map:
            flow_buttons = flow_map[flow_key].get("buttons", [])
            buttons.extend(flow_buttons)

         # In your Flask backend's /chat endpoint:
        return jsonify({
         "reply": reply,
         "buttons": buttons,
         "showButtons": len(buttons) > 0  # Add this line
         })

    except Exception as e:
     print("🔥 REAL ERROR:", str(e))  # print to terminal
     return jsonify({"error": "Something went wrong", "details": str(e)}), 500



# === Detect Button Intent ===
def detect_intent_and_generate_buttons(message):
    message_lower = message.lower().strip()

    # Keywords for each intent (strict and clear matches only)
    intent_keywords = {
        "contact": ["how can i contact", "get in touch", "contact you","im intrested", "reach you", "talk to someone", "connect with", "call you"],
        "email": ["send an email", "your email", "email address", "drop an email"],
        "whatsapp": ["whatsapp", "message on whatsapp", "chat on whatsapp"],
        "website": ["visit your website", "check your site", "open your site", "website link"]
    }

    buttons = []

    matched_intents = []

    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                matched_intents.append(intent)
                break  # stop after one match for this intent

    # Log for debugging
    print(f"[Intent Detection] Matched: {matched_intents} | Message: {message}")

    # If no intent matched, return no buttons
    if not matched_intents:
        return []

    # Add buttons only for matched intents
    if "whatsapp" in matched_intents or "contact" in matched_intents:
        buttons.append({
            "label": "WhatsApp",
            "type": "whatsapp",
            "value": "923137777404"
        })
    if "email" in matched_intents:
        buttons.append({
            "label": "Email Us",
            "type": "email",
            "value": "xcer.ai.team@gmail.com"
        })
    if "website" in matched_intents:
        buttons.append({
            "label": "Visit Website",
            "type": "url",
            "value": "https://xcerlabs.framer.website"
        })

    return buttons

    # === Custom Flow Logic ===
# === FLOW KEYWORDS (Global for detection) ===
flow_keywords = {
    "chatbots": ["chatbot", "bots", "ai bot", "lead bot", "assistant"],
    "marketing_tools": ["funnel", "landing page", "ads", "campaign", "marketing", "email", "conversion"],
    "social_media": ["social", "instagram", "facebook", "posts", "auto-posting", "content"]
}

flow_map = {
    "service_menu": {
        "reply": "\ud83c\udf1f *Welcome to XCER Labs!* \ud83c\udf1f\nWe offer cutting-edge digital solutions for your business:\n\n1. \ud83d\udcf1 *Social Media Automation* - AI-powered content & scheduling\n2. \ud83e\udd16 *Chatbot Solutions* - Smart conversational AI for businesses\n3. \ud83c\udfaf *Marketing Tools* - Funnels, campaigns & lead generation\n4. \ud83d\udccf *Website & CRM* - Custom development & integration\n5. \ud83e\uddf0 *E-commerce & Store Setup*\n6. \ud83d\udcca *Analytics & Insights*\n7. \u2728 *Brand Design Services*\n\nWhich service would you like to explore?",
        "buttons": [
            {"label": "Social Media", "type": "flow", "value": "social_media", "flow": True},
            {"label": "Chatbots", "type": "flow", "value": "chatbots", "flow": True},
            {"label": "Marketing Tools", "type": "flow", "value": "marketing_tools", "flow": True},
            {"label": "CRM/Website", "type": "flow", "value": "crm_website", "flow": True},
            {"label": "E-commerce", "type": "flow", "value": "ecommerce", "flow": True},
            {"label": "Design & Branding", "type": "flow", "value": "branding", "flow": True},
            {"label": "Talk to Expert", "type": "whatsapp", "value": "923137777404"}
        ]
    },

    "ecommerce": {
        "reply": "\ud83d\udece\ufe0f *E-commerce Solutions* \ud83d\udece\ufe0f\n\nWe help you launch your online store with:\n• Shopify / WordPress / Custom platforms\n• Product catalog & inventory setup\n• Cart recovery & automated emails\n• Payment & delivery integration\n• Analytics + Facebook Pixel setup\n• Speed optimization\n\nWant to see examples or get started?",
        "buttons": [
            {"label": "See Stores", "type": "url", "value": "https://xcerlabs.framer.website/stores"},
            {"label": "Book Demo", "type": "whatsapp", "value": "923137777404"},
            {"label": "Back to Menu", "type": "flow", "value": "service_menu", "flow": True}
        ]
    },

    "branding": {
        "reply": "\ud83c\udfa8 *Design & Branding Services* \ud83c\udfa8\n\nWe create impactful visuals for your business:\n• Logo & Identity Design\n• Brand Guidelines\n• Social Templates\n• Ads & Banners\n• Web UI/UX\n• Product Packaging\n• Motion Graphics\n\nNeed a brand that truly stands out?",
        "buttons": [
            {"label": "View Portfolio", "type": "url", "value": "https://xcerlabs.framer.website/design"},
            {"label": "Request Quote", "type": "email", "value": "xcer.ai.team@gmail.com"},
            {"label": "Back to Menu", "type": "flow", "value": "service_menu", "flow": True}
        ]
    },

    "social_media": {
        "reply": "🚀 *Social Media Automation Package* 🚀\n\nOur AI-driven solutions include:\n\n• \ud83d\udd25 *Auto-posting*: Schedule posts across FB/IG/LinkedIn\n• \ud83c\udfa8 *Content Creation*: AI-generated posts, reels & stories\n• \ud83d\udcca *Analytics Dashboard*: Track performance in real-time\n• \ud83d\udcc5 *Content Calendar*: Automated monthly planning\n• \ud83d\udcf8 *Hashtag Generator*: Optimized for maximum reach\n\nWhat would you like to know more about?",
        "buttons": [
            {"label": "Pricing Plans", "type": "flow", "value": "social_pricing", "flow": True},
            {"label": "See Examples", "type": "url", "value": "https://xcerlabs.framer.website/examples"},
            {"label": "Book Demo", "type": "whatsapp", "value": "923137777404"},
            {"label": "Main Menu", "type": "flow", "value": "service_menu", "flow": True}
        ]
    },

    "social_pricing": {
        "reply": "💰 *Social Media Pricing* 💰\n\n*Starter Plan* (Rs. 3,500/month)\n- 3 social platforms\n- 15 posts/month\n- Basic analytics\n\n*Pro Plan* (Rs. 7,500/month)\n- 5 platforms\n- 30 posts/month\n- Advanced analytics\n- Hashtag research\n\n*Enterprise Plan* (Custom)\n- Unlimited platforms\n- Dedicated account manager\n- Competitor analysis\n\nAll plans include AI content generation and scheduling tools.",
        "buttons": [
            {"label": "WhatsApp Us", "type": "whatsapp", "value": "923137777404"},
            {"label": "Email Inquiry", "type": "email", "value": "xcer.ai.team@gmail.com"},
            {"label": "Back to Social", "type": "flow", "value": "social_media", "flow": True},
            {"label": "Main Menu", "type": "flow", "value": "service_menu", "flow": True}
        ]
    },

    "chatbots": {
        "reply": "🤖 *AI Chatbot Solutions* 🤖\n\nWe build intelligent chatbots for:\n\n• \ud83d\udcb0 *Business Automation*: Lead gen, FAQs, customer support\n• \u2b50 *Influencers*: Fan engagement, course sales, DM automation\n• \ud83e\udd1d *Coaches*: Client onboarding, scheduling, Q&A\n• \ud83d\udee0 *Custom AI Agents*: With web access & API integrations\n\nWhich chatbot type interests you?",
        "buttons": [
            {"label": "Business Bot", "type": "flow", "value": "chatbot_business", "flow": True},
            {"label": "Influencer Bot", "type": "flow", "value": "chatbot_influencer", "flow": True},
            {"label": "Custom AI Agent", "type": "flow", "value": "chatbot_custom", "flow": True},
            {"label": "Pricing", "type": "flow", "value": "chatbot_pricing", "flow": True},
            {"label": "Main Menu", "type": "flow", "value": "service_menu", "flow": True}
        ]
    },

    "chatbot_business": {
        "reply": "🏢 *Business Chatbot Features* 🏢\n\nOur bots can:\n\n• Answer FAQs 24/7\n• Capture & qualify leads\n• Book appointments\n• Process orders\n• Integrate with your CRM\n• Provide multilingual support\n• Generate analytics reports\n\nPerfect for e-commerce, agencies, and service businesses!",
        "buttons": [
            {"label": "See Pricing", "type": "flow", "value": "chatbot_pricing", "flow": True},
            {"label": "Live Demo", "type": "whatsapp", "value": "923137777404"},
            {"label": "Back to Chatbots", "type": "flow", "value": "chatbots", "flow": True}
        ]
    },

    "chatbot_influencer": {
        "reply": "✨ *Influencer Chatbot Features* ✨\n\nSpecialized for content creators:\n\n• Auto-respond to DMs\n• Sell digital products/courses\n• Collect testimonials\n• Schedule consultations\n• Share exclusive content\n• Build email lists\n• Handle fan queries\n\nBoost your engagement while saving hours daily!",
        "buttons": [
            {"label": "See Demo Bot", "type": "whatsapp", "value": "923137777404"},
            {"label": "Pricing", "type": "flow", "value": "chatbot_pricing", "flow": True},
            {"label": "Back to Chatbots", "type": "flow", "value": "chatbots", "flow": True}
        ]
    },

    "chatbot_custom": {
        "reply": "⚡ *Custom AI Agent Capabilities* ⚡\n\nFor complex requirements:\n\n• Natural language processing\n• Web scraping/data extraction\n• Database integration\n• Custom API connections\n• Multi-platform deployment\n• Advanced analytics\n• Continuous learning\n\nTell us about your project!",
        "buttons": [
            {"label": "Consult Now", "type": "whatsapp", "value": "923137777404"},
            {"label": "Case Studies", "type": "url", "value": "https://xcerlabs.framer.website/cases"},
            {"label": "Back to Chatbots", "type": "flow", "value": "chatbots", "flow": True}
        ]
    },

    "chatbot_pricing": {
        "reply": "💵 *Chatbot Pricing Plans* 💵\n\n*Basic Bot* (Rs. 5,000/month)\n- 50 conversations/month\n- Basic FAQ responses\n- 1 platform\n\n*Advanced Bot* (Rs. 12,000/month)\n- 200 conversations\n- Lead capture\n- 3 platforms\n- Basic analytics\n\n*Enterprise Solution* (Custom)\n- Unlimited conversations\n- CRM integration\n- Custom development\n- Priority support\n\nAll prices exclude one-time setup fee.",
        "buttons": [
            {"label": "Get Quote", "type": "whatsapp", "value": "923137777404"},
            {"label": "Compare Plans", "type": "url", "value": "https://xcerlabs.framer.website/pricing"},
            {"label": "Back to Chatbots", "type": "flow", "value": "chatbots", "flow": True}
        ]
    },

    "marketing_tools": {
        "reply": "📈 *Powerful Marketing Tools* 📈\n\nWe provide:\n\n• High-converting sales funnels\n• Email/SMS automation\n• Landing page builder\n• Lead generation forms\n• Analytics integration\n• A/B testing tools\n• Retargeting solutions\n\nWhich tool would you like to explore?",
        "buttons": [
            {"label": "Sales Funnels", "type": "flow", "value": "funnels", "flow": True},
            {"label": "Email/SMS", "type": "flow", "value": "emailsms", "flow": True},
            {"label": "Landing Pages", "type": "flow", "value": "landing_pages", "flow": True},
            {"label": "Main Menu", "type": "flow", "value": "service_menu", "flow": True}
        ]
    },

    "funnels": {
        "reply": "🛍️ *Sales Funnel Features* 🛍️\n\nOur funnel solutions include:\n\n• Pre-built templates\n• Mobile-optimized design\n• Payment gateway integration\n• Upsell/downsell flows\n• Analytics dashboard\n• CRM synchronization\n• A/B testing\n\nConvert more visitors into customers!",
        "buttons": [
            {"label": "See Examples", "type": "url", "value": "https://xcerlabs.framer.website/funnels"},
            {"label": "Pricing", "type": "whatsapp", "value": "923137777404"},
            {"label": "Back to Tools", "type": "flow", "value": "marketing_tools", "flow": True}
        ]
    },

    "emailsms": {
        "reply": "✉️ *Email/SMS Automation* ✉️\n\nOur features:\n\n• AI-powered subject lines\n• Behavioral triggers\n• Drip campaigns\n• Personalization\n• Delivery optimization\n• Detailed analytics\n• Spam testing\n• List segmentation\n\nAutomate your communication!",
        "buttons": [
            {"label": "Book Demo", "type": "whatsapp", "value": "923137777404"},
            {"label": "Pricing Info", "type": "email", "value": "xcer.ai.team@gmail.com"},
            {"label": "Back to Tools", "type": "flow", "value": "marketing_tools", "flow": True}
        ]
    },

    "landing_pages": {
        "reply": "🖥️ *High-Converting Landing Pages* 🖥️\n\nWe offer:\n\n• Mobile-responsive designs\n• Fast loading speeds\n• Built-in lead capture\n• A/B testing\n• SEO optimized\n• Analytics integration\n• No-code editor\n• Template library\n\nGet more leads from your traffic!",
        "buttons": [
            {"label": "View Portfolio", "type": "url", "value": "https://xcerlabs.framer.website/web"},
            {"label": "Get Started", "type": "whatsapp", "value": "923137777404"},
            {"label": "Back to Tools", "type": "flow", "value": "marketing_tools", "flow": True}
        ]
    },

    "crm_website": {
        "reply": "🌐 *Website & CRM Solutions* 🌐\n\nOur services include:\n\n• Custom website development\n• E-commerce solutions\n• CRM setup (Hubspot, Zoho, Salesforce)\n• Booking system integration\n• Payment gateway setup\n• SEO optimization\n• Maintenance packages\n\nLet's build your digital presence!",
        "buttons": [
            {"label": "Website Examples", "type": "url", "value": "https://xcerlabs.framer.website/web"},
            {"label": "CRM Demo", "type": "whatsapp", "value": "923137777404"},
            {"label": "Get Quote", "type": "email", "value": "xcer.ai.team@gmail.com"},
            {"label": "Main Menu", "type": "flow", "value": "service_menu", "flow": True}
        ]
    }
}



def handle_flow_logic(message):
    key = message.replace("[FLOW] ", "").strip().lower()
    return flow_map.get(key, None)

if __name__ == '__main__':
    app.run(debug=True)
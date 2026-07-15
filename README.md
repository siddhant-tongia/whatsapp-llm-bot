<div align="center">
  <h1>📱 OpenAI WhatsApp Chatbot</h1>
  <p><strong>A powerful, context-aware Flask conversational API bridging WhatsApp (via Twilio) and LLMs (via Gemini/OpenAI endpoints)</strong></p>
</div>

<br/>

## 🌟 Overview

This project is a fully functional, production-ready WhatsApp chatbot backend. It exposes a Flask-based REST API that accepts user messages (both directly via API and via Twilio WhatsApp webhooks) and generates intelligent responses using Large Language Models. 

The bot is designed with **memory**, meaning it retains the conversation context for each unique user, enabling human-like, seamless, and context-aware interactions.

### ✨ Key Features
- **WhatsApp Integration:** Native integration with the Twilio WhatsApp API for seamless messaging.
- **Context-Aware Memory:** Maintains a conversation history dictionary so the AI remembers what was said earlier in the chat.
- **LLM Compatibility:** Powered by the OpenAI Python SDK pointing to Google's highly efficient Gemini API compatible endpoints.
- **Role-Based Prompts:** Easily switch behavior (e.g., Coaching Assistant) by utilizing System Prompts.
- **Conversation Management:** Export user chat histories directly into JSON files or clear them dynamically.
- **Deployment Ready:** Ships with a `Procfile` configured for `gunicorn`, ready to be deployed on platforms like Railway, Render, or Heroku.

---

## 🛠️ Tech Stack

- **Backend Framework:** Python & Flask
- **AI Integration:** OpenAI Python SDK & Google Gemini (gemini-1.5-flash)
- **WhatsApp API:** Twilio
- **Environment Management:** python-dotenv
- **Production Server:** Gunicorn

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd chat_bot
```

### 2. Install dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Set up your Environment Variables
Create a file named `.env` in the root of your folder and add your credentials:
```ini
# Google Gemini API Key (Accessible via Google AI Studio)
API_KEY=your_gemini_api_key_here

# Twilio Console Credentials
TWILIO_ACCOUNT_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here

# Twilio Sandbox Number (Must include the 'whatsapp:' prefix)
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```
*Your API will be running on `http://localhost:8080` (or `5000`).*

---

## 📞 Connecting to WhatsApp (Twilio Sandbox)

1. Sign up for a [Twilio Account](https://www.twilio.com/) and navigate to **Messaging > Try it out > Send a WhatsApp message**.
2. Connect your personal WhatsApp to the sandbox by sending the provided join code.
3. In Twilio, configure the **Sandbox Webhook URL** for incoming messages:
   - **For local testing:** Use a tool like [ngrok](https://ngrok.com/) to expose your local port (`ngrok http 8080`) and set your webhook to `https://<your-ngrok-url>/whatsapp`.
   - **For production:** Use your deployed domain (e.g., `https://your-railway-app.up.railway.app/whatsapp`).

---

## 🛣️ API Endpoints Reference

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check to verify the API is running. |
| `POST` | `/chat` | Standard REST API to chat with the bot. Requires JSON payload with `user_id` and `message`. |
| `POST` | `/whatsapp` | The Twilio Webhook URL to process incoming WhatsApp messages automatically. |
| `GET` | `/history/<user_id>` | Retrieves the entire conversation history for a specific user. |
| `POST`| `/clear/<user_id>` | Clears the memory/history of a specific user. |
| `GET` | `/analytics/<user_id>` | Retrieves messaging statistics for a specific user. |
| `GET` | `/analytics` | Retrieves global statistics (total users, total messages across the bot). |
| `GET` | `/export/<user_id>` | Downloads a `.json` file containing the user's conversation history. |
| `POST`| `/send_whatsapp` | Proactively trigger a WhatsApp message to a user. Requires `to_number` and `message`. |

---

## 🎓 What I Learned Building This

- Managing sensitive credentials using `.env` environment variables.
- How REST APIs function (distinguishing between `GET` and `POST` methods).
- Utilizing the OpenAI Python library with compatible endpoints (like Gemini).
- Engineering conversation memory for Large Language Models.
- Parsing and returning dynamic files (JSON data to bytes) for client downloads.
- Integrating Twilio's TwiML and Account SID/Auth Tokens to bridge Python to WhatsApp.
- Preparing a Flask application for production deployment using `gunicorn` and `Procfile`.

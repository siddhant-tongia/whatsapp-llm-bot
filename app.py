from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify, send_file
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from io import BytesIO
import json
import os

load_dotenv()

# create flask app
app = Flask(__name__)

# create Gemini client using OpenAI compatibility and environment variable
client = OpenAI(
    api_key = os.getenv("API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)
# empty conversations dictionary
conversations = {}

# Define system prompts for different business types
SYSTEM_PROMPTS = {
    "coaching": """You are a helpful admission assistant for XYZ Coaching Center Indore.

We offer coaching for:
- JEE (Main + Advanced)
- NEET (UG)

Common Information:
- Batches available: Morning (7am-10am), Afternoon (1pm-4pm), Evening (5pm-8pm)
- Admission season: Currently open for 2024-25 batch
- Faculty: Experienced faculty with 10+ years in JEE/NEET coaching
- Study Material: Comprehensive study material provided
- Test Series: Weekly and monthly tests included
- Results: Consistently producing top rankers every year

For PTM Booking:
- PTM is held every Saturday 10am-1pm
- To book a slot, share your name and ward's name
- Confirmation will be sent within 2 hours

Fee Structure:
- Detailed fee structure will be shared by our counselor
- EMI options available

Your behavior rules:
1. Be friendly, helpful and motivating
2. Keep responses short and suitable for WhatsApp
3. If asked something you don't know, say:
   "For more details, please call our reception at +91-9876543210. 
   We'll be happy to help!"
4. Never make up information about fees, results or faculty
5. Always encourage students to visit the center for demo class
"""
}

@app.route("/")
def home():
    return "Chatbot API is running "

# /chat route that accepts POST
@app.route("/chat",methods=['POST'])
def user_info():
    # get user_id and message from request
    data = request.json
    user_id = data.get('user_id')
    user_input = data.get('message')
    business_type = data.get('business_type', 'coaching')

    if not user_id or not user_input:
        return jsonify({"error": "Missing user_id or message"}), 400

    # if user is new, create dict with messages and business_type
    if user_id not in conversations:
        conversations[user_id] = {
            "messages": [],
            "business_type": business_type
        }

    # append user message to their list
    conversations[user_id]["messages"].append({"role": "user", "content": user_input})

    # Look up the business instructions
    system_prompt = SYSTEM_PROMPTS.get(business_type, "You are a helpful assistant")

    # call openai api with their message history
    try:
        full_messages = [{"role": "system", "content": system_prompt}] + conversations[user_id]["messages"]
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages = full_messages
        )
        # append assistant response to their list
        assistant_message = response.choices[0].message.content
        conversations[user_id]["messages"].append({"role": "assistant" , "content": assistant_message})

        # return response as json
        return jsonify({
            "user_id": user_id,
            "response": assistant_message,
            "business": business_type,
            "status": "SUCCESS"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /whatsapp route that accepts POST
@app.route("/whatsapp",methods=['POST'])
def whatsapp_webhook():
    # get user_id and message from request
    data = request.values
    user_input = data.get('Body', '').strip()
    user_id = data.get('From')
    business_type = "coaching"

    if not user_id or not user_input:
        return "Missing user_id or message", 400

    # if user is new, create dict with messages and business_type
    if user_id not in conversations:
        conversations[user_id] = {
            "messages": [],
            "business_type": business_type
        }

    # append user message to their list
    conversations[user_id]["messages"].append({"role": "user", "content": user_input})

    # Look up the business instructions
    system_prompt = SYSTEM_PROMPTS.get(business_type, "You are a helpful assistant")

    # call openai api with their message history
    try:
        full_messages = [{"role": "system", "content": system_prompt}] + conversations[user_id]["messages"]
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages = full_messages
        )
        # append assistant response to their list
        assistant_message = response.choices[0].message.content
        conversations[user_id]["messages"].append({"role": "assistant" , "content": assistant_message})

        # return response as TwiML
        twilio_response = MessagingResponse()
        twilio_response.message(assistant_message)
        return str(twilio_response)
        
    except Exception as e:
        twilio_response = MessagingResponse()
        twilio_response.message("Error: " + str(e))
        return str(twilio_response)

# /history route that accepts GET
@app.route("/history/<user_id>",methods=['GET'])
def get_history(user_id):
    if user_id in conversations:
        return jsonify({
            "user_id": user_id,
            "history": conversations[user_id]["messages"],
            "business_type": conversations[user_id]["business_type"]
        })
    return jsonify({"error": "User not Found"}),404

# /clear route that accepts POST
@app.route("/clear/<user_id>",methods=['POST'])
def clear_history(user_id):
    if user_id in conversations:
        conversations[user_id]["messages"] = []
        return jsonify({"status": "CLEARED"})
    return jsonify({"error": "User not Found"}),404

# /analytics route that accepts GET(stat of one specific user)
@app.route("/analytics/<user_id>",methods=['GET'])
def get_user_analytics(user_id):
    if user_id not in conversations:
        return jsonify({"Error": "User not found"}),404
    messages = conversations[user_id]["messages"]
    user_messages = [m for m in messages if m["role"] == "user"]
    return jsonify({
        "user_id": user_id,
        "total_conversation": len(user_messages),
        "total_message": len(messages),
        "business_type": conversations[user_id]["business_type"]
    })
# /analytics route that accepts GET(overall stat of all user)
@app.route("/analytics", methods=['GET'])
def get_analytics():
    total_messages = 0
    total_user_messages = 0
    for user_id in conversations:
        all_messages = conversations[user_id]["messages"]
        total_messages += len(all_messages)
        for m in all_messages:
            if m["role"] == "user":
                total_user_messages += 1
    return jsonify({
        "total_users": len(conversations),
        "total_user_messages": total_user_messages,
        "total_messages": total_messages,
    })
# /export route that accept GET
@app.route("/export/<user_id>",methods=['GET'])
def export(user_id):
    if user_id not in conversations:
        return jsonify({"Error": "User not found"}),404
    data = {"user_id": user_id, "message": conversations[user_id]["messages"]}
    json_data = json.dumps(data , indent=2)
    byte_file = BytesIO(json_data.encode())
    return send_file(
        byte_file,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"conversation_{user_id}.json"
    )
# Initialize the Twilio REST client using secure credentials stored in environment variables
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# /send_whatsapp route that accepts POST
@app.route("/send_whatsapp",methods=['POST'])
def send_whatsapp():
    data = request.json
    to_number = data.get('to_number')
    message = data.get('message')
    try:
        response = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=f"whatsapp:{to_number}"
        )
        return jsonify({
            "status": "SENT",
            "message_id": response.sid
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
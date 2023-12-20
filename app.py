from flask import Flask, request, jsonify
import requests
app = Flask(__name__)

# Dictionary to store conversation histories for different users
user_sessions = {}
import os
api_key = os.getenv("GEMINI_API_KEY")
generative_language_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + api_key

def generate_content(conversation):
    headers = {'Content-Type': 'application/json'}
    data = {"contents": conversation}
    
    response = requests.post(generative_language_url, headers=headers, json=data)
    #print("re",response.json())
    result = response.json()
    contents = result.get("candidates", [])[0].get("content",[]).get("parts", [])[0].get("text", "")
    return contents

@app.route('/', methods=['POST'])
def generate():
    user_id = request.json.get('user_id', '')
    user_input = request.json.get('user_input', '')

    # Get or create a conversation history for the user
    conversation_history = user_sessions.get(user_id, [])
    user_part = {"role": "user", "parts": [{"text": user_input}]}
    conversation_history.append(user_part)

    response_text = generate_content(conversation_history)

    model_part = {"role": "model", "parts": [{"text": response_text}]}
    conversation_history.append(model_part)

    # Update the conversation history for the user
    user_sessions[user_id] = conversation_history

    return jsonify({"response": response_text})

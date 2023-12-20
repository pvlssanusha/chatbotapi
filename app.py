from flask import Flask, request, jsonify
import requests
app = Flask(__name__)
from flask import render_template
from pymongo import MongoClient
# Dictionary to store conversation histories for different users
user_sessions = {}
import os
api_key = os.getenv("GEMINI_API_KEY")
generative_language_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + api_key
app.config['MONGO_URI'] = os.getenv("mongo_uri")

mongo = MongoClient(app.config['MONGO_URI'])
db = mongo.get_database('Usersessions')
collection = db.data
print(db)
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
    conversation_history=[]
    # Get or create a conversation history for the user
    res = db.data.find_one({"userid": user_id})
    #print("res",res)
    if res:
        conversation_history =res.get("history")
        #print("ch",conversation_history)
          # Replace 'my_collection' with your collection name
    else:
        datavalues={
            "userid":user_id,
            "history":conversation_history
        }
        collection.insert_one(datavalues)
    user_part = {"role": "user", "parts": [{"text": user_input}]}
    conversation_history.append(user_part)

    response_text = generate_content(conversation_history)

    model_part = {"role": "model", "parts": [{"text": response_text}]}
    conversation_history.append(model_part)
    #print(conversation_history,user_id)
    filter_criteria = {"userid":user_id}

# Specify the update operation (e.g., set a new value for a field)
    update_operation = {"$set": {"history":conversation_history}}

# Perform the update for a single document
    result = collection.update_one(filter_criteria, update_operation)
    db.chat.insert_one(
    {"userid": user_id, "history":conversation_history})
    

    return jsonify({"history":conversation_history})

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import json
import subprocess

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rimon1610',  # Change with DB password
    'database': 'chatbot_db',
    'cursorclass': pymysql.cursors.DictCursor
}

# Database connection helper
def get_db_connection():
    return pymysql.connect(**db_config)

# User registration
@app.route('/register', methods=['POST'])
def register():
    print("i am here register")
    data = request.json
    print(data)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    password_hash = password 

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except pymysql.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        if 'conn' in locals():
            conn.close()

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"error": "Missing username or password"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

        if user and user['password_hash'] == password:
            # No session, so just return success message and user info if you want
            return jsonify({"message": "Login successful", "user": {"id": user['id'], "username": user['username']}}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except pymysql.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Save conversation (user_id must be passed in request now, since no session)
@app.route('/save-conversation', methods=['POST'])
def save_conversation():
    data = request.json
    user_id = data.get('user_id')
    conversation_data = data.get('conversation')
    print(data)

    if not user_id or not conversation_data:
        return jsonify({"error": "Missing user_id or conversation data"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO conversations (user_id, conversation_data) VALUES (%s, %s)",
                (user_id, json.dumps(conversation_data))
            )
            conn.commit()
        
        return jsonify({"message": "Conversation saved successfully"}), 201
    except pymysql.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Load conversations (user_id must be passed as query param or header)
@app.route('/get-conversations', methods=['GET'])
def get_conversations():
    print("i am getting")
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, conversation_data, created_at, updated_at FROM conversations WHERE user_id = %s ORDER BY id",
                (user_id,)
            )
            conversations = cursor.fetchall()
        print(conversations)
        return jsonify({"conversations": conversations}), 200
    except pymysql.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Chat endpoint that proxies message to Rasa server
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        rasa_response = requests.post(
            'http://localhost:5005/webhooks/rest/webhook',
            json={"sender": "user", "message": user_message}
        )
        rasa_response.raise_for_status()
        rasa_data = rasa_response.json()
        return jsonify({"responses": rasa_data})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to contact Rasa server", "details": str(e)}), 500

# Upload PDF endpoint
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():

    try:
        UPLOAD_FOLDER = '../uploads'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        file.filename = "file.pdf"
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        print(file_path)
        return jsonify({"responses": "file Uploaded"}), 200
    except:
        jsonify({"response":"Can not upload file."})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

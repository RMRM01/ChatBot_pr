from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import requests
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import subprocess

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Secret key for session management
app.secret_key = os.urandom(24)

# Optional: Configure session cookie for cross-origin if needed
# (Uncomment and adjust if you use HTTPS)
# app.config.update(
#     SESSION_COOKIE_SAMESITE="None",
#     SESSION_COOKIE_SECURE=True,
# )
# Database configuration

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Rimon161@0',  # Change to your DB password
    'database': 'chatbot_db',
    'cursorclass': pymysql.cursors.DictCursor
}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Database connection helper
def get_db_connection():
    return pymysql.connect(**db_config)

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
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
    print("Login data:", data)
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
        print("User fetched:", user)
        print(user['password_hash']+ password)
        if user and user['password_hash'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({"message": "Login successful"}), 200
        else:
            print("Invalid credentials")
            return jsonify({"error": "Invalid credentials"}), 401
    except pymysql.Error as err:
        print("DB Error:", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# User logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

# Check authentication status
@app.route('/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "username": session.get('username')
        }), 200
    return jsonify({"authenticated": False}), 200

# Save conversation
@app.route('/save-conversation', methods=['POST'])
def save_conversation():
    data = request.json
    conversation_data = data.get('conversation')
    
    if not conversation_data:
        return jsonify({"error": "No conversation data provided"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO conversations (user_id, conversation_data) VALUES (%s, %s)",
                (session['user_id'], json.dumps(conversation_data))
            )
            conn.commit()
        return jsonify({"message": "Conversation saved successfully"}), 201
    except pymysql.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Load conversations
@app.route('/get-conversations', methods=['GET'])
def get_conversations():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, conversation_data, created_at, updated_at FROM conversations WHERE user_id = %s ORDER BY updated_at DESC",
                (session['user_id'],)
            )
            conversations = cursor.fetchall()
        return jsonify({"conversations": conversations}), 200
    except pymysql.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Chat endpoint that proxies message to Rasa server
@app.route('/chat', methods=['POST'])
def chat():
    print("Function triggered")
    data = request.json
    

    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    # else:
    #     return jsonify({"response": "good"}), 200

    try:
        rasa_response = requests.post(
            'http://localhost:5005/webhooks/rest/webhook',
            json={"sender": "user", "message": user_message}
        )
        rasa_response.raise_for_status()

        rasa_data = rasa_response.json()
        print("Rasa replied with:", rasa_data)

        return jsonify({"responses": rasa_data})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to contact Rasa server", "details": str(e)}), 500



# --------- UP load pdf 



@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    UPLOAD_FOLDER = './uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    file.filename="file.pdf"
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    print(file_path)
    return jsonify({"responses": "file Uploaded"}),200
# reading the file 

    # main_file.run_full_pipeline()
    # # chunks = making_chunk(file_path)
  
    
    # # After pipeline runs
    # subprocess.run(["rasa", "train"], check=True)

    # #getting latest modell
    # latest_model = get_latest_model()
    # if latest_model:
    #     response = requests.put("http://localhost:5005/model", json={"model_file": latest_model})
    #     print("Model reload response:", response.status_code)

    # chunks=[]
    # rasa_responses = []
    # for chunk in chunks:
    #     rasa_response = requests.post(
    #         'http://localhost:5005/webhooks/rest/webhook',
    #         json={"sender": "user", "message": chunk}
    #     )
    #     rasa_responses.append(rasa_response.json())

    # return jsonify({"responses": rasa_responses})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

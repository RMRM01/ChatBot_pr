from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import main_file
import subprocess

# from making_chunk import making_chunk
def get_latest_model(path="models"):
    files = [f for f in os.listdir(path) if f.endswith(".tar.gz")]
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(os.path.join(path, f)), reverse=True)
    return os.path.join(path, files[0])



app = Flask(__name__)
CORS(app)


UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    file.filename="file.pdf"
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
# reading the file 

    main_file.run_full_pipeline()
    # chunks = making_chunk(file_path)
  
    
    # After pipeline runs
    subprocess.run(["rasa", "train"], check=True)

    #getting latest modell
    latest_model = get_latest_model()
    if latest_model:
        response = requests.put("http://localhost:5005/model", json={"model_file": latest_model})
        print("Model reload response:", response.status_code)

    chunks=[]
    rasa_responses = []
    for chunk in chunks:
        rasa_response = requests.post(
            'http://localhost:5005/webhooks/rest/webhook',
            json={"sender": "user", "message": chunk}
        )
        rasa_responses.append(rasa_response.json())

    return jsonify({"responses": rasa_responses})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    rasa_response = requests.post(
        'http://localhost:5005/webhooks/rest/webhook',
        json={"sender": "user", "message": user_message}
    )

    return jsonify({"responses": rasa_response.json()})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
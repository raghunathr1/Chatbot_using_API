from flask import Flask, request, jsonify
import os
import uuid
import google.generativeai as genai

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Gemini
genai.configure(api_key="AIzaSyABV1ud5-exnr66FoMXZWEzwhOXgh4xCxU")
model = genai.GenerativeModel("gemini-2.5-flash")

# In-memory session storage
sessions = {}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 🔥 READ FILE CONTENT HERE
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        file_text = f.read()

    session_id = str(uuid.uuid4())

    # 🔥 STORE FILE CONTENT, NOT PATH
    sessions[session_id] = {
        "filename": file.filename,
        "content": file_text
    }

    return jsonify({
        "message": "File uploaded and read successfully",
        "session_id": session_id
    })


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get("session_id")
    question = data.get("question")

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session_id"}), 400

    file_text = sessions[session_id]["content"]

    prompt = f"""
Answer the question strictly based on the file content.

File Content:
{file_text}

Question:
{question}
"""

    response = model.generate_content(prompt)

    return jsonify({
        "answer": response.text
    })
    

if __name__ == "__main__":
    app.run(debug=True)

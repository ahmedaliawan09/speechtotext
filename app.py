from flask import Flask, request, jsonify, render_template
import os
import whisper
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

model = whisper.load_model("base")

# ✅ New route to serve the HTML page
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Transcribe audio with automatic language detection
    result = model.transcribe(filepath, task="translate")  # Automatically detects language and translates to English

    os.remove(filepath)

    return jsonify({"transcription": result["text"]})


if __name__ == "__main__":
    app.run(debug=True)

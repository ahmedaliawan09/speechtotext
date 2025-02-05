import time
import os
from flask import Flask, request, jsonify, send_from_directory
import whisper
from werkzeug.utils import secure_filename
from gtts import gTTS
import ffmpeg

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load the Whisper model
model = whisper.load_model("medium")


# Function to extract audio from video files
def extract_audio_from_video(video_filepath):
    # Generate a temporary audio file path
    audio_filepath = video_filepath.rsplit(".", 1)[0] + ".mp3"
    # Use FFmpeg to extract audio
    ffmpeg.input(video_filepath).output(audio_filepath).run()
    return audio_filepath

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Language selected by the user for transcription
    language = request.form.get("language", "en")  # Default to English if no language is selected

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # If the file is a video, extract audio from it
    if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        audio_filepath = extract_audio_from_video(filepath)
        os.remove(filepath)  # Remove the video file after extracting audio
    else:
        audio_filepath = filepath

    # Transcribe the audio in the selected language using Whisper
    result = model.transcribe(audio_filepath, language=language, task="transcribe")

    # Remove the audio file after transcription
    os.remove(audio_filepath)

    # Generate a unique audio file name based on the current time and language
    timestamp = str(int(time.time()))  # Use current timestamp for uniqueness
    audio_filename = f"{timestamp}_{language}_transcription.mp3"
    audio_filepath = os.path.join(app.config["UPLOAD_FOLDER"], audio_filename)

    # Convert the transcribed text into speech using gTTS (Google Text-to-Speech)
    tts = gTTS(text=result["text"], lang=language, slow=False)
    tts.save(audio_filepath)

    # Check if the audio file exists before returning the URL
    if not os.path.exists(audio_filepath):
        return jsonify({"error": "Audio file creation failed."}), 500

    # Return the transcription and the audio file URL
    return jsonify({
        "transcription": result["text"],
        "audio_url": f"/uploads/{audio_filename}"  # URL to access the audio file
    })

@app.route("/uploads/<filename>")
def get_audio_file(filename):
    # Serve the audio file so it can be accessed by Streamlit
    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(audio_path):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)

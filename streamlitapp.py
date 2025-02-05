import streamlit as st
import requests

# Set up the Streamlit interface
st.title("Audio Transcription with Language Selection")

# File uploader
audio_file = st.file_uploader("Upload an audio or video file", type=["mp3", "wav", "m4a", "ogg", "mp4", "avi", "mov", "mkv"])

# Language selection
language = st.selectbox("Select language for transcription", ["en", "es", "fr", "de", "it", "pt", "ur"])

# Button to submit the form
if st.button("Transcribe"):
    if audio_file:
        # Convert the uploaded file to a BytesIO object
        files = {"file": audio_file.getvalue()}
        data = {"language": language}
        
        # Make a POST request to Flask API
        response = requests.post("http://127.0.0.1:5000/transcribe", files=files, data=data)
        
        if response.status_code == 200:
            # Display the transcription result
            result = response.json()
            st.subheader("Transcription:")
            st.write(result.get("transcription"))
            
            # Display the audio player for the updated audio file
            audio_url = result.get("audio_url")
            st.audio(f"http://127.0.0.1:5000{audio_url}")  # Correct URL for Streamlit to access the new audio
        else:
            st.error(f"Error: {response.json().get('error')}")
    else:
        st.warning("Please upload an audio or video file.")

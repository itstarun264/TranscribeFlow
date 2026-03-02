import whisper

print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded ✅")

def transcribe_audio(audio_path):
    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        return f"Transcription failed: {str(e)}"
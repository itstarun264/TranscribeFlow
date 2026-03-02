import whisper
import os

print("Loading Whisper model...")
model = whisper.load_model("base", device="cpu")
print("Model loaded successfully ✅")

def transcribe_audio(audio_file):
    print(f"Transcribing: {audio_file} ...")
    
    if not os.path.exists(audio_file):
        print("❌ Audio file not found!")
        return None

    result = model.transcribe(audio_file, fp16=False)
    return result["text"]


if __name__ == "__main__":
  
    audio_file = "harvard.wav"

    text = transcribe_audio(audio_file)

    if text:
        print("\n📝 Transcribed Text:\n")
        print(text)

        txt_filename = audio_file + ".txt"
        with open(txt_filename, "w", encoding="utf-8") as file:
            file.write(text)

        print(f"\n Transcription saved to: {txt_filename}")

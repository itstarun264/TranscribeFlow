import os

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg", "m4a"}

USERNAME = "tarun"
PASSWORD = "123"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

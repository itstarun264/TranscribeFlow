from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os
import json
from werkzeug.utils import secure_filename

from config import *
from asr import transcribe_audio
from summarizer import summarize_text

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        return "Invalid username or password ❌"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/index", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    transcript = None
    summary = None
    transcript_filename = None
    summary_filename = None
    json_filename = None

    if request.method == "POST":
        file = request.files.get("audio")

        if not file or file.filename == "":
            return "No file selected ❌"

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # Process
            transcript = transcribe_audio(file_path)
            summary = summarize_text(transcript)

            base_name = os.path.splitext(filename)[0]

            # Save Transcript
            transcript_filename = f"{base_name}_transcript.txt"
            transcript_path = os.path.join(app.config["UPLOAD_FOLDER"], transcript_filename)

            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)

            # Save Summary
            summary_filename = f"{base_name}_summary.txt"
            summary_path = os.path.join(app.config["UPLOAD_FOLDER"], summary_filename)

            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary)

            # Save JSON (NEW)
            json_filename = f"{base_name}_result.json"
            json_path = os.path.join(app.config["UPLOAD_FOLDER"], json_filename)

            json_data = {
                "transcript": transcript,
                "summary": summary
            }

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4)

        else:
            return "Invalid file type ❌"

    return render_template(
        "index.html",
        transcript=transcript,
        summary=summary,
        transcript_file=transcript_filename,
        summary_file=summary_filename,
        json_file=json_filename
    )


# ---------------- DOWNLOAD ----------------
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# ---------------- JSON API ----------------
@app.route("/upload", methods=["POST"])
def upload_api():
    file = request.files.get("audio")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    transcript = transcribe_audio(file_path)
    summary = summarize_text(transcript)

    return jsonify({
        "transcript": transcript,
        "summary": summary
    })


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
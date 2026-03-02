from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename

from config import *
from asr import transcribe_audio
from summarizer import summarize_text
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        return "Invalid username or password ❌"

    return render_template("login.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    transcript = None
    summary = None
    summary_filename = None
    transcript_filename = None

    if request.method == "POST":
        file = request.files.get("audio")

        if not file or file.filename == "":
            return "No file selected ❌"

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            transcript = transcribe_audio(file_path)
            summary = summarize_text(transcript)

            # Save transcript
            transcript_file_path = file_path + "_transcript.txt"
            with open(transcript_file_path, "w", encoding="utf-8") as f:
                f.write(transcript)

            # Save summary
            summary_file_path = file_path + "_summary.txt"
            with open(summary_file_path, "w", encoding="utf-8") as f:
                f.write(summary)

            summary_filename = os.path.basename(summary_file_path)
            transcript_filename = os.path.basename(transcript_file_path)

        else:
            return "Invalid file type ❌"

    return render_template(
        "index.html",
        transcript=transcript,
        summary=summary,
        summary_file=summary_filename,
        transcript_file=transcript_filename
    )
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# JSON API endpoint (Milestone requirement)
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


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
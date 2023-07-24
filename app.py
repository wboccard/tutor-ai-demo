from flask import Flask, render_template, url_for, request, flash, redirect, send_file
from werkzeug.utils import secure_filename
# from chatbot import get_ai_response
from improved_chatbot import Chatbot
import os
import subprocess
import time

UPLOAD_FOLDER = 'static\\uploads'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'the random string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
google_chatbot = Chatbot()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/audioUpload", methods=["GET","POST"])
def print_audio():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        initial_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        final_file = os.path.join(app.config["UPLOAD_FOLDER"], "fixed.flac")
        subprocess.call(["ffmpeg.exe", "-hide_banner", "-loglevel", "error", "-y", "-i", initial_file,
                         "-codec", "flac", final_file])
        with open(os.path.join(app.config['UPLOAD_FOLDER'], "fixed.flac"), "rb") as question:
            audio = question.read()
            ai_answer = google_chatbot.get_ai_response(audio)
            print(ai_answer)
        return redirect(url_for('index'))
    return "File saved"

@app.route('/<audio_file_name>')
def returnAudioFile(audio_file_name):
    time.sleep(2)
    path_to_audio_file = os.path.join(app.config['UPLOAD_FOLDER'], audio_file_name)
    return send_file(
        path_to_audio_file,
        mimetype="audio/mp3",
        as_attachment=True,
        download_name="output.mp3"
    )

if __name__ == "__main__":
    app.run(debug=True)
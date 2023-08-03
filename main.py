from flask import Flask, render_template, url_for, request, flash, redirect, send_file, send_from_directory
from werkzeug.utils import secure_filename
# from chatbot import get_ai_response
from improved_chatbot import Chatbot
import os
import subprocess

UPLOAD_FOLDER = os.path.join("static", "uploads")
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'the random string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
google_chatbot = Chatbot()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/audioUpload", methods=["POST"])
def print_audio():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    file_audio = file.read()
    pipe = subprocess.Popen(
        'ffmpeg -i pipe: -f flac pipe:'
        .split(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    audio, _ = pipe.communicate(file_audio)
    speech_to_text = google_chatbot.get_speech_to_text(audio)
    if not speech_to_text:
        speech_to_text = "Woops, I didn't say anything!"
        return speech_to_text
    speech_to_text = speech_to_text[0].upper() + speech_to_text[1:] + "?"
    return speech_to_text

@app.route('/askChat', methods=["POST"])
def askChatbot():
    request_json = request.get_json()
    try:
        answer = google_chatbot.ask_chat(request_json['question'])
    except:
        answer = "An error occured."
    return answer

@app.route('/retrieveSpeech', methods=['POST'])
def get_speech():
    request_json = request.get_json()
    audio = google_chatbot.text_to_speech(request_json['text_to_speech'])
    return audio

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
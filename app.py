from flask import Flask, render_template, url_for, request, flash, redirect, send_file, send_from_directory
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

@app.route("/audioUpload", methods=["POST"])
def print_audio():
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
        speech_to_text = google_chatbot.get_speech_to_text(audio)
    if not speech_to_text:
        speech_to_text = "Woops, I didn't say anything!"
        return speech_to_text
    speech_to_text = speech_to_text[0].upper() + speech_to_text[1:] + "?"
    return speech_to_text

@app.route('/askChat', methods=["POST"])
def askChatbot():
    request_json = request.get_json()
    # print(request_json['question'])
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

# @app.route('/<audio_file_name>')
# def returnAudioFile(audio_file_name):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], audio_file_name)

if __name__ == "__main__":
    app.run(debug=True)
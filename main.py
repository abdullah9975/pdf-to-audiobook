import os
import PyPDF2
import pyttsx3
from flask import Flask, render_template, request, send_file, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to convert text to speech
def convert_text_to_speech(text, audio_file):
    engine.save_to_file(text, audio_file)
    engine.runAndWait()


def get_download_status(audio_file):
    audio_file_path = os.path.join(app.config['AUDIO_FOLDER'], audio_file)
    if os.path.exists(audio_file_path):
        return 'completed'
    else:
        return 'failed'


# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and conversion
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file uploaded", 'error')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", 'error')
        return redirect(request.url)
    if file:
        pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_file_path)
        pdf_reader = PyPDF2.PdfReader(pdf_file_path)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        audio_file = os.path.splitext(file.filename)[0] + '.mp3'
        audio_file_path = os.path.join(app.config['AUDIO_FOLDER'], audio_file)
        convert_text_to_speech(text, audio_file_path)
        flash("File downloaded successfully", 'success')
        return redirect(url_for('index'))

# Route to fetch the progress of the file download
@app.route('/progress')
def progress():
    audio_file = request.args.get('audio_file')
    audio_file_path = os.path.join(app.config['AUDIO_FOLDER'], audio_file)
    if os.path.exists(audio_file_path):
        file_size = os.path.getsize(audio_file_path)
        return {'progress': file_size}
    else:
        return {'progress': 0}

# Route to fetch the status of the download
@app.route('/status')
def status():
    audio_file = request.args.get('audio_file')
    return {'status': get_download_status(audio_file)}

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Serve index.html
@app.route('/')
def index():
    return render_template('index.html')

# Handle Excel upload (no file processing here)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # File handling logic here (you can store the file temporarily)
        return 'File uploaded successfully!'

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
import requests
import base64
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import ObjectIdentifier
from pyasn1.codec.der.decoder import decode
from pyasn1.type import univ
import re
import pandas as pd
import random

app = Flask(__name__)

# Base URL for fetching tenders
base_tender_url = 'https://public-api.prozorro.gov.ua/api/2.5/tenders/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form['language']
    return redirect(url_for('home', language=lang))

@app.route('/home/<language>')
def home(language):
    messages = {
        'en': "Hello, my name is Vitoriia, nice to see you on my website. I welcome you to visit all three case studies and thank you for your attention.",
        'fr': "Bonjour, je m'appelle Vitoriia, ravi de vous voir sur mon site. Je vous invite à découvrir les trois études de cas et vous remercie de votre attention.",
        'de': "Hallo, mein Name ist Vitoriia, schön dich auf meiner Website zu sehen. Ich lade dich ein, alle drei Fallstudien zu besuchen, und danke dir für deine Aufmerksamkeit."
    }
    message = messages.get(language, messages['en'])
    return render_template('home.html', language=language, message=message)

@app.route('/case_study_1')
def case_study_1():
    # Your code for Case Study 1 (Tender Info App)
    return render_template('case_study_1.html')

@app.route('/case_study_2')
def case_study_2():
    # This will render the page with Excel file and the ability to edit
    excel_file_path = r'C:\Users\Asus\PycharmProjects\internship_start\S&P 500 Capitalization.xlsx'
    df = pd.read_excel(excel_file_path)
    return render_template('case_study_2.html', tables=[df.to_html(classes='data')])

@app.route('/case_study_3')
def case_study_3():
    # Probability game logic (simple random guessing game)
    random_number = random.randint(1, 10)
    return render_template('case_study_3.html', number=random_number)

if __name__ == '__main__':
    app.run(debug=True)

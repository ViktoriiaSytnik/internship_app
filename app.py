from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd

app = Flask(__name__)

# Base URL for fetching tenders
base_tender_url = 'https://public-api.prozorro.gov.ua/api/2.5/tenders/'

# Landing page route
@app.route('/')
def index():
    return render_template('index.html')

# Setting the language and redirecting to the home page
@app.route('/set_language/<language>')
def set_language(language):
    return redirect(url_for('home', language=language))

# Home page based on selected language
@app.route('/home/<language>')
def home(language):
    messages = {
        'en': "Hello, my name is Vitoriia, nice to see you on my website. I welcome you to visit all three case studies and thank you for your attention.",
        'fr': "Bonjour, je m'appelle Vitoriia, ravi de vous voir sur mon site. Je vous invite à découvrir les trois études de cas et vous remercie de votre attention.",
        'de': "Hallo, mein Name ist Vitoriia, schön dich auf meiner Website zu sehen. Ich lade dich ein, alle drei Fallstudien zu besuchen, und danke dir für deine Aufmerksamkeit."
    }
    message = messages.get(language, messages['en'])
    return render_template('home.html', language=language, message=message)

# Case Study 1
@app.route('/case_study_1')
def case_study_1():
    return render_template('case_study_1.html')

# Case Study 2 - Excel Data
@app.route('/case_study_2')
def case_study_2():
    excel_file_path = r'C:\Users\Asus\PycharmProjects\internship_start\S&P 500 Capitalization.xlsx'
    df = pd.read_excel(excel_file_path)
    return render_template('case_study_2.html', tables=[df.to_html(classes='data')])

# Case Study 3 - Random Number Game
@app.route('/case_study_3')
def case_study_3():
    random_number = random.randint(1, 10)
    return render_template('case_study_3.html', number=random_number)

if __name__ == '__main__':
    app.run(debug=True)

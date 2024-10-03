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
        'en': "Thank you for landing on my page and your time. My name is Sytnik Viktoriia, I am a student at FH des BFI Wien and I made this website myself (programming is my hobby). I also love data analytics, fighting financial crime and creative solutions. On the page below you can find examples of my projects. Have a great time!",
        'fr': "Merci d'avoir atterri sur ma page et de m'avoir consacré du temps. Je m'appelle Sytnik Viktoria, j'étudie à la FH des BFI Wien et j'ai créé ce site web moi-même (la programmation est mon hobby). J'aime aussi analyse des données, la lutte contre la criminalité financière et les solutions créatives. Sur la page ci-dessous, vous trouverez des exemples de mes projets. Je vous souhaite de passer un bon moment !",
        'de': "Danke, dass du hier vorbeigeschaut hast und dir Zeit nimmst. Ich bin die Victoria Sytnik, studiere an der FH des BFI in Wien und hab diese Webseite selbst gestaltet (Programmieren ist mein Hobby). Außerdem bin ich verrückt nach data analytik, der Bekämpfung von Finanzkriminalität und finde kreative Lösungen super. Unten auf der Seite findest du Beispiele meiner Projekte. Ich wünsch dir eine tolle Zeit!"
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

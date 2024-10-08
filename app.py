import os

from flask import Flask, render_template, request, redirect, url_for, send_file
import random
import pandas as pd
import requests
import base64
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import ObjectIdentifier
from pyasn1.codec.der.decoder import decode
from pyasn1.type import univ
import re

app = Flask(__name__)

# Base URL for fetching tenders
base_tender_url = 'https://public-api.prozorro.gov.ua/api/2.5/tenders/'


# Function to decode base64 if needed
def decode_base64_if_needed(data):
    try:
        decoded_data = base64.b64decode(data)
        return decoded_data
    except base64.binascii.Error:
        return data


# Function to parse EDRPOU/RNOKPP strings
def parse_edrpou_string(input_string):
    sequences = input_string.split('\n\n')
    dicts = []
    for sequence in sequences:
        if sequence.strip():
            current_dict = {}
            lines = sequence.split('\n')
            current_field = None
            for line in lines:
                if 'Sequence:' in line or 'SetOf:' in line:
                    continue
                match = re.match(r'\s*(field-\d+)=(.*)', line)
                if match:
                    current_field = match.group(1)
                    current_dict[current_field] = match.group(2).strip()
                elif current_field:
                    current_dict[current_field] += ' ' + line.strip()
            dicts.append(current_dict)
    return dicts


# Function to extract PKCS#7 content
def extract_pkcs7_content(pkcs7_data):
    try:
        pkcs7_obj = pkcs7.load_der_pkcs7_certificates(pkcs7_data)
        if pkcs7_obj:
            for cert in pkcs7_obj:
                subject = cert.subject

                # Custom OID for EDRPOU/RNOKPP
                edrp_rnokpp_object_id = ObjectIdentifier('2.5.29.9')
                try:
                    edrp_rnokpp_extension = cert.extensions.get_extension_for_oid(edrp_rnokpp_object_id)
                    edrp_rnokpp_raw_value = edrp_rnokpp_extension.value.value
                    decoded_edrp_rnokpp, _ = decode(edrp_rnokpp_raw_value, asn1Spec=univ.Sequence())
                    parsed_edrp_rnokpp = parse_edrpou_string(str(decoded_edrp_rnokpp.prettyPrint()))
                    edrp_result = parsed_edrp_rnokpp[0]['field-0'].split()[-1]
                    rnokpp_result = parsed_edrp_rnokpp[1]['field-0'].split()[-1]
                except x509.ExtensionNotFound:
                    edrp_result = None
                    rnokpp_result = None

                # Helper function to extract attributes
                def get_attribute(name, oid):
                    try:
                        return name.get_attributes_for_oid(oid)[0].value
                    except IndexError:
                        return None

                signer_info = {
                    "РНОКПП": rnokpp_result,
                    "Код ЄДРПОУ": edrp_result,
                    "Посада": get_attribute(subject, x509.ObjectIdentifier("2.5.4.12")),
                    "ПІБ": get_attribute(subject, x509.NameOID.COMMON_NAME),
                    "Організація": get_attribute(subject, x509.NameOID.ORGANIZATION_NAME),
                }

                return signer_info
        else:
            return None
    except Exception as e:
        return None


# Function to download file
def download_file(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content, response.headers.get('Content-Type')
        else:
            return None, None
    except requests.exceptions.RequestException:
        return None, None


# Function to process signature
def process_signature(url):
    file_data, mime_type = download_file(url)
    if file_data:
        decoded_data = decode_base64_if_needed(file_data)
        signer_info = extract_pkcs7_content(decoded_data)
        return signer_info
    else:
        return None


# Function to process the tender
def process_tender(tender_id):
    tender_url = f"{base_tender_url}{tender_id}"
    response = requests.get(tender_url)
    if response.status_code == 200:
        tender_data = response.json()

        # Extract procuring entity details
        procuring_entity = tender_data.get('data', {}).get('procuringEntity', {})
        procuring_entity_id = procuring_entity.get('identifier', {}).get('id', '')
        procuring_entity_contact_name = procuring_entity.get('contactPoint', {}).get('name', '')

        result = f"<h3>Company`s Information:</h3>"
        result += f"<p><strong>Procuring Entity ID:</strong> {procuring_entity_id}</p>"
        result += f"<p><strong>Contact Name:</strong> {procuring_entity_contact_name}</p>"

        # Extract documents from tender data
        for doc in tender_data.get('data', {}).get('documents', []):
            if doc.get('documentType') == 'notice' and doc.get('format') == 'application/pkcs7-signature':
                signature_url = doc['url']
                signer_info = process_signature(signature_url)
                if signer_info:
                    result += "<h3>Signer`s data:</h3>"
                    result += f"<p><strong>Tax Number:</strong> {signer_info.get('РНОКПП')}</p>"
                    result += f"<p><strong>Organisation`s code:</strong> {signer_info.get('Код ЄДРПОУ')}</p>"
                    result += f"<p><strong>Profession:</strong> {signer_info.get('Посада')}</p>"
                    result += f"<p><strong>Name/Surname:</strong> {signer_info.get('ПІБ')}</p>"
                    result += f"<p><strong>Organisation:</strong> {signer_info.get('Організація')}</p>"
                else:
                    result += f"<p>Signature processing failed for Tender ID: {tender_id}</p>"
        return result
    else:
        return f"<p>Не вдалося отримати дані тендера з ID {tender_id}. Статус-код: {response.status_code}</p>"


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
        'en': "Thank you for landing on my page and your time. My name is Sytnik Viktoriia, I am currently a student in the European Economy and Business Management programme. I made this website myself (programming is my hobby). I also love data analytics, fighting financial crime, and finding creative solutions to complex challenges. On the page below you can find examples of my projects. Have a great time exploring!",

        'fr': "Merci d'avoir atterri sur ma page et pour votre temps. Je m'appelle Sytnik Viktoria, je suis actuellement étudiante dans le programme d'Économie Européenne et Gestion d'Entreprise. J'ai créé ce site web moi-même (la programmation est mon passe-temps). J'aime aussi l'analyse de données, la lutte contre la criminalité financière et trouver des solutions créatives aux défis complexes. Sur la page ci-dessous, vous pouvez trouver des exemples de mes projets. Passez un excellent moment à explorer !",

        'de': "Danke, dass Sie auf meiner Seite gelandet sind und für Ihre Zeit. Mein Name ist Sytnik Victoria, ich bin derzeit Studentin im Programm für Europäische Wirtschaft und Unternehmensführung. Ich habe diese Website selbst erstellt (Programmieren ist mein Hobby). Ich liebe auch Datenanalyse, die Bekämpfung von Finanzkriminalität und das Finden kreativer Lösungen für komplexe Herausforderungen. Auf der Seite unten finden Sie Beispiele meiner Projekte. Viel Spaß beim Erkunden!"
    }
    message = messages.get(language, messages['en'])
    return render_template('home.html', language=language, message=message)



@app.route('/my_photo')
def my_photo():
    image_path = os.path.join(os.getcwd(), 'templates', 'my_photo.png')
    return send_file(image_path, mimetype='image/png')


@app.route('/photo_case1')
def photo_case1():
    image_path = os.path.join(os.getcwd(), 'templates', 'transparency_ua.png')
    return send_file(image_path, mimetype='image/png')


# Case Study 1 - Tender Processing
@app.route('/case_study_1', methods=['GET', 'POST'])
def case_study_1():
    result = ""
    if request.method == 'POST':
        tender_ids = request.form['tender_ids'].split()
        for tender_id in tender_ids:
            result += process_tender(tender_id) + "<br><br>"
    return render_template('case_study_1.html', result=result)


# Case Study 2 - Excel Data
@app.route('/case_study_2')
def case_study_2():
    # No need to load any Excel file, just render the HTML with the embedded Google Sheet.
    return render_template('case_study_2.html')


@app.route('/logo')
def logo():
    image_path = os.path.join(os.getcwd(), 'templates', 'logo.png')
    return send_file(image_path, mimetype='image/png')


@app.route('/pdf')
def pdf():
    pdf_path = os.path.join(os.getcwd(), 'templates', 'business&science report draft en.pdf')
    return send_file(pdf_path, mimetype='application/pdf')


@app.route('/case_study_3')
def case_study_3():
    random_number = random.randint(1, 10)
    return render_template('case_study_3.html', number=random_number)


if __name__ == '__main__':
    app.run(debug=True)

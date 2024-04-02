from flask import Flask, jsonify, request
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# instantiate the app
app = Flask(__name__)

def sendEmail(subject, body, to_email):
    from_email = "lailiaofishery@gmail.com"
    password = "msvs brgi hzhe mtbw"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    subject = request.json.get('subject', '')
    body = request.json.get('body', '')
    to_email = request.json.get('to_email', '')
    sendEmail(subject, body, to_email)
    return jsonify({'status': 'Email sent'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5015, debug=True)


    
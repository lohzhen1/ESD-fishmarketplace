from flask import Flask, jsonify, request
from flask_cors import CORS

from twilio.rest import Client

# instantiate the app
app = Flask(__name__)

def sendSMS(body_message):
    twilio_account_sid = 'AC1b77fa8c87f235e9a7b28706dd8481a9'
    twilio_auth_token = "d27ac42d38ffabb39c7efdea6a68c544"
    twilio_phone_number = '+13187193338'
 
    # Send an SMS
    client = Client(twilio_account_sid, twilio_auth_token)
    message = client.messages.create(
        body=body_message,
        from_=twilio_phone_number,
        to='+65 9658 2035'  # Replace with your actual phone number
    )

@app.route('/send_sms', methods=['POST'])
def send_sms_endpoint():
    body_message = request.json.get('body_message', '')
    sendSMS(body_message)
    return jsonify({'status': 'SMS sent'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5014, debug=True)
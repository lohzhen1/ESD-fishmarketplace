from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
import requests
import os

app = Flask(__name__)
CORS(app)

# This is to run from azure database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

sms_url = os.getenv('SMS_URL', 'http://sms:5014/send_sms')
payment_url = os.getenv('PAYMENT_URL', 'http://payment:5011/payment/refund')
print(os.getenv('PAYMENT_URL'))

# use it for setting up locally without docker
#order_URL = "http://localhost:5009/order"
#refund_URL = "http://localhost:5002/refund"

#docker URL 
order_URL = "http://order:5009/order"
refund_URL = "http://refund:5002/refund"


@app.route('/get_refund/<string:refundID>', methods=['GET'])
def get_refund(refundID):
    url_get_refund = f'{refund_URL}/{refundID}'
    response_get_refund = requests.get(url_get_refund)

    if response_get_refund.status_code == 200:
        refund = response_get_refund.json()['data']
        return jsonify({"code": 200, "message": "Refund retrieved successfully.", "data": refund}), 200
    else:
        return jsonify({"code": 404, "message": "Failed to retrieve refund."}), 404


@app.route('/update_refund/<string:refundID>', methods=['PUT'])
def update_refund(refundID):
    data = request.get_json()

    refundStatus = data.get('refundStatus')
    orderStatus = data.get('orderStatus')

    # Get orderID from refund
    url_get_refund = f'{refund_URL}/{refundID}'
    response_get_refund = requests.get(url_get_refund)
    print(refund_URL)
    print(url_get_refund)

    if response_get_refund.status_code != 200:
        return jsonify({"code": 500, "message": "Failed to retrieve refund."}), 500

    refund = response_get_refund.json()['data']
    orderID = refund['orderID']

    # Get order details
    url_get_order = f'{order_URL}/{orderID}'
    response_get_order = requests.get(url_get_order)

    if response_get_order.status_code != 200:
        return jsonify({"code": 500, "message": "Failed to retrieve order."}), 500

    order = response_get_order.json()['data']
    checkoutID = order['checkoutID']

    # Make a POST request to the /refund route


    # this is the actual URL of your payment service
    
    refund_url = payment_url
    
    
    #refund_url = 'http://localhost:5011/refund'  # replace with the actual URL of your payment service
    response = requests.post(refund_url, json={'checkoutID': checkoutID})

    # Check the response status
    if response.status_code != 200:
    # if response["code"] != 200:
        return jsonify({"code": 500, "message": "Failed to create refund."}), 500

    # Update refund status
    url_update_refund = f'{refund_URL}/{refundID}'
    response_update_refund = requests.put(url_update_refund, json={'refundStatus': refundStatus})

    if response_update_refund.status_code != 200:
        return jsonify({"code": 500, "message": "Failed to update refund status."}), 500

    # Update order status
    print(order_URL)
    url_update_order = f'{order_URL}/{orderID}'
    print(url_update_order)
    response_update_order = requests.put(url_update_order, json={'status': orderStatus})

    if response_update_order.status_code != 200:
        return jsonify({"code": 500, "message": "Failed to update order status."}), 500

    # Send SMS to user
    data = {'body_message': 'Refund Result is completed, Please login into your account to check the refund status. Thank you!'}
    
    # without docker setup
    #response = requests.post('http://localhost:5014/send_sms', json=data)
    
    # with docker seutup
    response = requests.post(sms_url, json=data)
    if response.status_code == 200:
        print('SMS sent successfully.')
    else:
        print('Failed to send SMS.')

    return jsonify({"code": 200, "message": "Refund and order status updated successfully."}), 200




# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200, debug=True)

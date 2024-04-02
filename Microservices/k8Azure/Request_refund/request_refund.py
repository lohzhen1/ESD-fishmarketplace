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

# use it for setting up locally without docker
#order_URL = "http://localhost:5009/order"
#refund_URL = "http://localhost:5002/refund"

sms_url = os.getenv('SMS_URL', 'http://sms:5014/send_sms')
email_url = os.getenv('EMAIL_URL', 'http://email:5015/send_email')


order_URL = "http://order:5009/order"
refund_URL = "http://refund:5002/refund"



@app.route('/request_refund/<int:orderID>', methods=['POST'])
def request_refund(orderID):
    # Define the URL of the get_orders_by_user route in order.py
    url_get_orders = f'{order_URL}/{orderID}'

    # Make the GET request
    response_get_orders = requests.get(url_get_orders)

    # Print the response of the GET request
    print(f'Response of GET request: {response_get_orders.text}')

    # Check the response
    if response_get_orders.status_code == 200:
        print('Order retrieved successfully.')
        order = response_get_orders.json()['data']  # Get the order data

        # Define the URL of the create_refund route in refund.py
        url_create_refund = refund_URL

        # Define the data you want to send in the POST request
        post_data = order  # Assign the order data to the post_data variable
        post_data['description'] = request.json.get('description', 'Your description here')  # Get the description from the request data
        post_data['pic'] = request.json.get('pic', 'https://esdimage.blob.core.windows.net/mysql-image/refund_image_0f5fc850-47ee-4d51-9fa9-5b50769ba6fa')  # Get the picture URL from the request data
        post_data['refundStatus'] = 'Pending'
        # Make the POST request
        response_create_refund = requests.post(url_create_refund, json=post_data)

        # Print the response of the POST request
        print(f'Response of POST request: {response_create_refund.text}')

        # Check the response
        if response_create_refund.status_code == 201:
            print(f'Refund created successfully for order {order["orderID"]}.')

            # Update the order status
            order['status'] = 'Refunding in Progress'
            url_update_order = f'{order_URL}/{orderID}'
            response_update_order = requests.put(url_update_order, json=order)

            if response_update_order.status_code == 200:
                print(f'Order status updated successfully for order {order["orderID"]}.')

                send_notification()

            else:
                print(f'Failed to update order status for order {order["orderID"]}.')
        else:
            print(f'Failed to create refund for order {order["orderID"]}.')
        
        return jsonify({"code": 200, "message": "Refund request processed."}), 200
    else:
        print('Failed to retrieve order.')
        return jsonify({"code": 404, "message": "Failed to retrieve order."}), 404



def send_notification():
    # Send SMS to supplier
    sms_data = {'body_message': 'A new refund has been requested from the user. Please login and check the refund status.'}
    sms_response = requests.post(sms_url, json=sms_data)

    # this is for localhost without the docker setup
    #sms_response = requests.post('http://localhost:5014/send_sms', json=sms_data)

    # Send email to supplier
    email_data = {
        'subject': 'Refund Requested',
        'body': 'A new refund has been requested from the user. Please login and check the refund status.',
        'to_email': 'zxloh.2022@scis.smu.edu.sg'
    }
    email_response = requests.post(email_url, json=email_data)

    #this is for localhost without docker setup
    #email_response = requests.post('http://localhost:5015/send_email', json=email_data)


    
    # Check responses
    if sms_response.status_code == 200 and email_response.status_code == 200:
        print('SMS and Email sent successfully.')
    else:
        if sms_response.status_code != 200:
            print('Failed to send SMS.')
        if email_response.status_code != 200:
            print('Failed to send Email.')




# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)

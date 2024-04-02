from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

import pika
import json

from uuid import uuid4
from datetime import datetime 
from os import environ

app = Flask(__name__)
CORS(app)

# checkoutURL = "http://localhost:5011/create-checkout-session"
# orderDetailURL = "http://localhost:5050/order/allDetails/"
# orderURL = "http://localhost:5009/order/info/"

checkoutURL = environ.get('checkoutURL') or "http://localhost:5011/create-checkout-session"
orderURL = environ.get('orderURL') or "http://localhost:5009/order/info/"
orderDetailURL = environ.get('orderDetailURL') or "http://localhost:5050/order/allDetails/"

@app.route("/handleAuctionPayment", methods=['POST'])
def handle_auction_payment():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            order = request.get_json()

            print("\nReceived an auctions in JSON:", order)

            result = handlePayment(order)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "handle_auction_payment.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def handlePayment(order):

    orderDetails = invoke_http(orderDetailURL + str(order["orderID"]), method='GET')

    code = orderDetails["code"]

    print("\nOrder details:",orderDetails)

    
    if code == 200:
        paymentResult = invoke_http(checkoutURL, method='POST', json=orderDetails["data"])

        print("\nReceived an payment in JSON:",paymentResult)

        sessionID = paymentResult["sessionId"]

        if sessionID :
            return {
                "code": 201,
                "message": 'Bid success',
                "data": {
                    "sessionID": sessionID,
                    "orderID": str(order["orderID"]),
                }
            }
        else:
            return {
                "code": 500,
                "message": "Payment failed."
            }
    else:
        return {
            "code": 500,
            "message": "Payment failed."
        }

#update order
# def updateOrder():
#     #call update order
#     updatedOrder = {
#         "orderID": order["orderID"],
#         "status": "Completed",
#         "paymentMethod": "Stripe",
#         "checkoutID": sessionID
#     }
#     orderResult = invoke_http(orderURL + str(order["orderID"]), method='PUT', json=updatedOrder)
#     code = orderResult["code"]
#     if code == 200:
#         return {
#             "code": 201,
#             "message": 'Bid success'
#         }
#     else:
#         return {
#             "code": 500,
#             "message": "Payment failed."
#         }  

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an auctions...")
    app.run(host="0.0.0.0", port=5101, debug=True)

    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

import pika
import json

from uuid import uuid4
import sched
import time
from datetime import datetime, timezone
import threading
from os import environ

app = Flask(__name__)
CORS(app)

# auctionURL = "http://localhost:5007/auction"
# orderURL = "http://localhost:5009/order"
# orderDetailsURL = "http://localhost:5050/order/details"

auctionURL = environ.get('auctionURL') or "http://localhost:5007/auction" 
orderURL = environ.get('orderURL') or"http://localhost:5009/order"
orderDetailsURL = environ.get('orderDetailsURL') or "http://localhost:5050/order/details"
smsURL = environ.get('smsURL') or "http://localhost:5014/send_sms" 
emailURL = environ.get('emailURL') or "http://localhost:5015/send_email"

scheduler = sched.scheduler(time.time, time.sleep)

def get_auctionEnd():
    auctionToday = invoke_http(auctionURL + "/today", method='GET')
    print('Auction Today:', auctionToday['data']['auction'])

    # dateTime_Obj = datetime.strptime(auctionToday['data']['auction'][0]['timeEnd'], "%a, %d %b %Y %H:%M:%S %Z")
    # specific_time = dateTime_Obj.timestamp()
    # scheduler.enterabs(specific_time, 1, checkSettlement, ())
    
    # Create a separate thread for the scheduler
    # scheduler_thread = threading.Thread(target=scheduler.run)

    # Start the scheduler thread
    # scheduler_thread.start()
    # scheduler.run()
    specific_time = time.time() + 5
    

# get_auctionEnd()

def checkSettlement():
    print("done")

@app.route("/endAuction", methods=['POST'])
def end_auction():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            auctions = request.get_json()
            # current_datetime = datetime.now()

            # formatted_datetime_str = current_datetime.strftime("%a, %d %b %Y %H:%M:%S %Z")
            # formatted_datetime = datetime.strptime(datetime.now(), "%a, %d %b %Y %H:%M:%S %Z")


            print("\nReceived an auctions in JSON:", auctions)

            result = processEndAuction(auctions)
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
                "message": "place_bid.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processEndAuction(auctions):

    endAuctionResult = invoke_http(auctionURL + "/end", method='PUT', json=auctions)

    print(endAuctionResult)

    code = endAuctionResult["code"]

    if code == 200:
        #call create order
        for auction in auctions:
            order_data = {
                "userID": auction["winnerID"],
                "orderedTime": datetime.now(timezone.utc).isoformat(),
                "paymentMethod": "",
                "deliveryAddress": "",
                "totalPrice": auction["currentPrice"],
                "status": "Pending Payment",
                "supplierID": 3,
                "supplierName": "Ah Tan Pte Ltd",
                "checkoutID": "",
            }
            orderResult = invoke_http(orderURL, method='POST', json=order_data)
            print(orderResult)

            updateAuctionInfo = {
                "orderID": orderResult["data"]["orderID"]
            }
            auctionResult = invoke_http(auctionURL + "/updateOrder/" + str(auction["auctionID"]), method='PUT', json=updateAuctionInfo)
            print(auctionResult)

            orderDetailsInfo = {
                "orderID": orderResult["data"]["orderID"],
                "fishID": auction["fishID"],
                "qty": 1,
                "subTotal": auction["currentPrice"],
                "itemName": auction["itemName"],
            }
            orderDetailsResult = invoke_http(orderDetailsURL, method='POST', json=orderDetailsInfo)
            print(orderDetailsResult)

            # Send SMS to user
            data = {'body_message': 'You have won an auction, Please login into your account and proceed with the payment. Thank you!'}
            
            # without docker setup
            response = invoke_http(smsURL, method='POST', json=data)

            email_data = {
                'subject': 'Auction Result',
                'body': 'You have won an auction, Please login into your account and proceed with the payment. Thank you!',
                'to_email': 'zxloh.2022@scis.smu.edu.sg'
            }
            email_response = invoke_http(emailURL, method='POST', json=email_data)

            # with docker seutup
            #response = requests.post(sms_url, json=data)
            if response["status"] == 'SMS sent':
                print('SMS sent successfully.')
            else:
                print('Failed to send SMS.')
        return {
            "code": 201,
            "message": 'Auction end success',
            "data": {
                "orderID": orderResult["data"]["orderID"],
            }
        }
    else:
        return {
            "code": 500,
            "message": "Auction end failed."
        }
    pass



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an auctions...")
    app.run(host="0.0.0.0", port=5102, debug=True)

    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

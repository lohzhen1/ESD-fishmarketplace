from flask import Flask, jsonify
from flask_cors import CORS

import os, sys

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
# biddingURL = "http://localhost:5008/bidding_records"
auctionURL = environ.get('auctionURL') or "http://localhost:5007/auction"
orderURL = environ.get('orderURL') or"http://localhost:5009/order"
orderDetailsURL = environ.get('orderDetailsURL') or "http://localhost:5050/order/details"
biddingURL = environ.get('biddingURL') or "http://localhost:5008/bidding_records"
smsURL = environ.get('smsURL') or "http://localhost:5014/send_sms" 
emailURL = environ.get('emailURL') or "http://localhost:5015/send_email"

@app.route("/checkSettlement", methods=['GET'])
def check_settlement():
    # Simple check of input format and data of the request are JSON
    try:
        result = checkAuctionSettlement()
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




def checkAuctionSettlement():
    auctionResult = invoke_http(auctionURL + "/today", method='GET')

    code = auctionResult["code"]
    print(auctionResult)
    if code == 200:
        #call create order
        for auction in auctionResult["data"]["auction"]:

            orderResult = invoke_http(orderURL + "/" + str(auction["orderID"]), method='GET')

            code = orderResult["code"]
            if code == 200:
                
                print(orderResult)
                if orderResult["data"]["status"] == "Completed":
                    continue
                else:
                    biddingResult = invoke_http(biddingURL + "/auction/" + str(auction["auctionID"]), method='GET')
                    print(biddingResult)

                    biddingArr = biddingResult["data"]

                    if len(biddingArr) > 1:

                        user = {
                            "userID": biddingArr[1]["bidderID"]
                        }
                        updateOrder = invoke_http(orderURL + "/user/" + str(auction["orderID"]), method='PUT', json=user)

                        if updateOrder["code"] != 200:
                            return {
                                "code": 500,
                                "message": "Settlement process failed."
                            }
                        else:
                            updateAuction = {
                                "bidderID": biddingArr[1]["bidderID"],
                                "bidderName": biddingArr[1]["bidderName"],
                                "biddingPrice": biddingArr[1]["biddingPrice"]
                            }
                            updateAuctionResult = invoke_http(auctionURL + "/bidding/" + str(auction["auctionID"]), method='PUT', json=updateAuction)
                            if updateAuctionResult["code"] != 200:
                                return {
                                        "code": 500,
                                        "message": "Settlement process failed."
                                    }
                            else:
                                # Send SMS to user
                                data = {'body_message': 'You have won an auction, Please login into your account and proceed with the payment. Thank you!'}
                                
                                # # without docker setup
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
                                continue

        return {
            "code": 201,
            "message": 'All settlement has been checked and updated',
        }
    else:
        return {
            "code": 500,
            "message": "Settlement process failed."
        }
    pass



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for checking settlement...")
    app.run(host="0.0.0.0", port=5106, debug=True)


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import ForeignKey, TIMESTAMP, desc
from flask_socketio import SocketIO, emit
import datetime
from uuid import uuid4
import amqp_connection
import json
import pika
from threading import Thread
from os import environ

app = Flask(__name__)
CORS(app)

#This is to run from azure database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)

# a_queue_name = 'Record_Bid' # queue to be subscribed by Activity_Log microservice
a_queue_name = environ.get('a_queue_name') or 'Record_Bid' # queue to be subscribed by Error microservice


##to run locally (assuming you have phpmyadmin table all set up)
##app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/bidding_records'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins='*')

class bidding_records(db.Model):

     # this is azure sql server table
    __tablename__ = 'bidding_records'
    biddingRecordID = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Auction Record ID
    auctionID = db.Column(db.Integer, nullable=False)  # Auction ID
    bidderID = db.Column(db.Integer, nullable=False)  # Bidder ID
    bidderName = db.Column(db.String, nullable=False)  # Bidder ID
    biddingPrice = db.Column(db.Float, nullable=False)  # Bidding Price
    bidTime = db.Column(db.DateTime, nullable=False)  # Bidding Price


    # Initialize AuctionRecord object
    def __init__(self, biddingRecordID ,auctionID, bidderID, biddingPrice, bidderName):
        self.biddingRecordID = biddingRecordID  # Set auction ID
        self.auctionID = auctionID  # Set auction ID
        self.bidderID = bidderID  # Set bidder ID
        self.biddingPrice = biddingPrice  # Set bidding price
        self.bidTime = datetime.datetime.now()  # Set bidding price
        self.bidderName = bidderName  # Set bidding price


# Method to return all the auction records by using GET method
@app.route("/bidding_records", methods=['GET'])
def get_all_bidding_records():
    auction_record_list = db.session.query(bidding_records).all()  # Query all auction records

    if len(auction_record_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bidding_records": [{"biddingRecordID": record.biddingRecordID, "auctionID": record.auctionID, 
                                       "bidderID": record.bidderID, "biddingPrice": record.biddingPrice, "bidTime": record.bidTime
                                       , "bidderName": record.bidderName}
                                      for record in auction_record_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no auction records."
        }
    ), 404

# Method to return the specific auction record by using biddingRecordID
@app.route("/bidding_records/<int:biddingRecordID>", methods=['GET'])
def find_by_biddingRecordID(biddingRecordID):
    record = db.session.query(bidding_records).get(biddingRecordID)

    if record:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "biddingRecordID": record.biddingRecordID, 
                    "auctionID": record.auctionID,
                    "bidderID": record.bidderID, 
                    "biddingPrice": record.biddingPrice,
                    "bidTime": record.bidTime,
                    "bidderName": record.bidderName
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Auction record not found."
        }
    ), 404

@app.route("/bidding_records/auction/<int:auctionID>", methods=['GET'])
def find_by_auctionID(auctionID):
    records = db.session.query(bidding_records).filter(bidding_records.auctionID == auctionID).order_by(desc(bidding_records.biddingPrice)).all()

    if records:
        return jsonify(
            {
                "code": 200,
                "data": [{
                    "biddingRecordID": record.biddingRecordID, 
                    "auctionID": record.auctionID,
                    "bidderID": record.bidderID, 
                    "biddingPrice": record.biddingPrice,
                    "bidTime": record.bidTime,
                    "bidderName": record.bidderName
                } for record in records]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bidding record not found."
        }
    ), 404

# Create AuctionRecord by using POST
@app.route("/bidding_records", methods=['POST'])
def create_bidding_record():
    data = request.get_json()
    biddingRecordID = str(uuid4().int)
    biddingRecordID = int(biddingRecordID[0:8])
    
    while db.session.query(bidding_records).get(biddingRecordID):
        biddingRecordID = str(uuid4().int)
        biddingRecordID = int(biddingRecordID[0:8])
        # return jsonify(
        #     {
        #         "code": 400,
        #         "data": {
        #             "biddingRecordID": biddingRecordID
        #         },
        #         "message": "Auction record already exists."
        #     }
        # ), 400

    record = bidding_records(biddingRecordID, data['auctionID'], data['bidderID'], data['biddingPrice'], data["bidderName"])

    try:
        db.session.add(record)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "biddingRecordID": biddingRecordID
                },
                "message": "An error occurred creating the auction record."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": {
                "biddingRecordID": record.biddingRecordID, 
                "auctionID": record.auctionID,
                "bidderID": record.bidderID, 
                "biddingPrice": record.biddingPrice,
                "biddingPrice": record.bidTime,
                "bidderName": record.bidderName
            }
        }
    ), 201

@app.route("/bidding_records/<int:auctionID>", methods=['POST'])
def add_bid(auctionID):
    try:
        # update status
        data = request.get_json()
        auction = db.session.query(bidding_records).filter(bidding_records.auctionID == data['auctionID']).order_by(desc(bidding_records.biddingPrice)).limit(1)
        
        if not auction:
            if data:
                try:
                    record = bidding_records(data['auctionID'], data['bidderID'], data['biddingPrice'], data["bidderName"])
                    db.session.add(record)
                    db.session.commit()
                except:
                    return jsonify(
                        {
                            "code": 500,
                            "data": {
                                "auctionID": auctionID
                            },
                            "message": "An error occurred creating the auction record."
                        }
                    ), 500
                
                emit_update(data)

                return jsonify(
                    {
                        "code": 201,
                        "data": {
                            "auctionID": record.auctionID,
                            "bidderID": record.bidderID, 
                            "biddingPrice": record.biddingPrice,
                            "bidTime": record.bidTime,
                            "bidderName": record.bidderName
                        }
                    }
                ), 201
        else:
            if data:
                if float(data['biddingPrice']) > float(auction.biddingPrice):

                    try:
                        record = bidding_records(data['auctionID'], data['bidderID'], data['biddingPrice'], data["bidderName"])
                        db.session.add(record)
                        db.session.commit()
                    except:
                        return jsonify(
                            {
                                "code": 500,
                                "data": {
                                    "auctionID": auctionID
                                },
                                "message": "An error occurred creating the auction record."
                            }
                        ), 500
                    
                    emit_update(data)

                    return jsonify(
                        {
                            "code": 201,
                            "data": {
                                "auctionID": record.auctionID,
                                "bidderID": record.bidderID, 
                                "biddingPrice": record.biddingPrice,
                                "bidTime": record.bidTime,
                                "bidderName": record.bidderName
                            }
                        }
                    ), 201
                
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "auctionID": auctionID,
                },
                "message": "An error occurred while updating the auction. " + str(e)
            }
        ), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Emit real-time updates to the connected clients
def emit_update(data):
    socketio.emit('update', data)

def receiveAuctionBid(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=a_queue_name, on_message_callback=callback, auto_ack=True)
        print('Auction_Bid: Consuming from queue:', a_queue_name)
        thread = Thread(target = channel.start_consuming)
        thread.start() # an implicit loop waiting to receive messages;
             #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"Auction_Bid: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("Auction_Bid: Program interrupted by user.") 

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nauction_bid: Received an auction bid by " + __file__)
    processBid(json.loads(body))
    print()

def processBid(auctionInfo):
    with app.app_context():
        data = auctionInfo
        biddingRecordID = str(uuid4().int)
        biddingRecordID = int(biddingRecordID[0:8])
        
        while db.session.query(bidding_records).get(biddingRecordID):
            biddingRecordID = str(uuid4().int)
            biddingRecordID = int(biddingRecordID[0:8])
            # return jsonify(
            #     {
            #         "code": 400,
            #         "data": {
            #             "biddingRecordID": biddingRecordID
            #         },
            #         "message": "Auction record already exists."
            #     }
            # ), 400
        print(data)
        record = bidding_records(biddingRecordID, data['auctionID'], data['winnerID'], data['currentPrice'], data["winnerName"])
        try:
            db.session.add(record)
            db.session.commit()
        except:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "biddingRecordID": biddingRecordID
                    },
                    "message": "An error occurred creating the bidding record."
                }
            ), 500

        return jsonify(
            {
                "code": 201,
                "data": {
                    "biddingRecordID": record.biddingRecordID, 
                    "auctionID": record.auctionID,
                    "bidderID": record.bidderID, 
                    "biddingPrice": record.biddingPrice,
                    "bidTime": record.bidTime,
                    "bidderName": record.bidderName
                }
            }
        ), 201

@app.route("/bidding_records/delete", methods=['DELETE'])
def delete_all_bids():

    num_rows_deleted = db.session.query(bidding_records).delete()

    biddingRecordID = str(uuid4().int)
    biddingRecordID = int(biddingRecordID[0:8])
    
    while db.session.query(bidding_records).get(biddingRecordID):
        biddingRecordID = str(uuid4().int)
        biddingRecordID = int(biddingRecordID[0:8])

    record = bidding_records(biddingRecordID, '1', '1', '20', 'John Doe')
    db.session.add(record)

    biddingRecordID = str(uuid4().int)
    biddingRecordID = int(biddingRecordID[0:8])
    
    while db.session.query(bidding_records).get(biddingRecordID):
        biddingRecordID = str(uuid4().int)
        biddingRecordID = int(biddingRecordID[0:8])

    record = bidding_records(biddingRecordID, '2', '1', '20', 'John Doe')
    db.session.add(record)
    db.session.commit()

    return jsonify(
        {
            "code": 200,
            "message": str(num_rows_deleted) + " bids deleted"
        }
    )


print("Record_Bid: Getting Connection")
connection = amqp_connection.create_connection() #get the connection to the broker
print("Record_Bid: Connection established successfully")
channel = connection.channel()
receiveAuctionBid(channel) 
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)



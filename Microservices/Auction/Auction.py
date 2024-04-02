from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from sqlalchemy import ForeignKey, TIMESTAMP
from flask_socketio import SocketIO, emit
from uuid import uuid4
import amqp_connection
import json
import pika
from threading import Thread
from os import environ

app = Flask(__name__)
CORS(app)

# a_queue_name = 'Auction_Bid' # queue to be subscribed by Activity_Log microservice
a_queue_name = environ.get('a_queue_name') or 'Auction_Bid' # queue to be subscribed by Error microservice

##to run locally (assuming you have phpmyadmin table all set up)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/auction'


#This is to run from azure database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins='*')

class Auction(db.Model):
    ##__tablename is to indicate the azure database
    __tablename__ = 'Auction'
    auctionID = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Auction ID
    fishID = db.Column(db.Integer, nullable=False)  # Fish ID
    winnerID = db.Column(db.Integer, nullable=True)  # Winner ID
    orderID = db.Column(db.Integer, nullable=True)  # Winner ID
    winnerName = db.Column(db.String(100), nullable=True)  # Winner Name
    itemName = db.Column(db.String(100), nullable=True)  # item Name
    currentPrice = db.Column(db.Float, nullable=False)  # Current Price
    timestart = db.Column(TIMESTAMP, nullable=False)  # Time Start
    timeEnd = db.Column(TIMESTAMP, nullable=False)  # Time End

    status = db.Column(db.String(50), nullable=False)  # Status

    # Initialize Auction object
    def __init__(self, auctionID, fishID, winnerID, winnerName, currentPrice, timestart, status, timeEnd, itemName, orderID):
        self.auctionID = auctionID  # Set auction ID
        self.fishID = fishID  # Set fish ID
        self.winnerID = winnerID  # Set winner ID
        self.orderID = orderID  # Set winner ID
        self.winnerName = winnerName  # Set winner name
        self.itemName = itemName  # Set item name
        self.currentPrice = currentPrice  # Set current price
        self.timestart = timestart  # Set time start
        self.timeEnd = timeEnd  # Set time end
        self.status = status  # Set status


#route to the root directory
@app.route('/')

#method to return the number of auction in azure database
def index():
    auctions = Auction.query.all()
    return 'Number of auctions: %d' % len(auctions)


# Method to return all the auction items by using GET method
@app.route("/auction", methods=['GET'])
def get_all_auction_items():
    auction_list = db.session.query(Auction).all()  # Query all auction items

    if len(auction_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "auction": [{"auctionID": auction.auctionID, "fishID": auction.fishID,
                                 "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                                 "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                                 "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                                 "status": auction.status} 
                                for auction in auction_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no auction items."
        }
    ), 404

# Method to return all the auction items by using GET method
@app.route("/auction/today", methods=['GET'])
def get_today_auction_items():
    today = datetime.now().date()
    auction_list = db.session.query(Auction).filter(db.cast(Auction.timestart, db.Date) == today).all()  # Query all auction items

    print(auction_list)
    # if len(auction_list):
    return jsonify(
        {
            "code": 200,
            "data": {
                "auction": [{"auctionID": auction.auctionID, "fishID": auction.fishID,
                                "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                                "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                                "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                                "status": auction.status, "orderID": auction.orderID} 
                            for auction in auction_list]
            }
        }
    )
    # return jsonify(
    #     {
    #         "code": 404,
    #         "message": "There are no auction items.",
    #         "data": []
    #     }
    # ), 404

# Method to return the specific auction item by using auctionID
@app.route("/auction/<int:auctionID>", methods=['GET'])
def find_by_auctionID(auctionID):
    auction = db.session.query(Auction).get(auctionID)

    if auction:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "auctionID": auction.auctionID, "fishID": auction.fishID,
                    "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                    "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                    "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                    "status": auction.status
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Auction item not found."
        }
    ), 404

# Create Auction by using POST
@app.route("/auction", methods=['POST'])
def create_auction_item():
    data = request.get_json()
    # auctionID = data['auctionID']
    # if db.session.query(Auction).get(auctionID):
    #     return jsonify(
    #         {
    #             "code": 400,
    #             "data": {
    #                 "auctionID": auctionID
    #             },
    #             "message": "Auction item already exists."
    #         }
    #     ), 400
    auctionID = str(uuid4().int)
    auctionID = int(auctionID[0:5])

    auction = Auction(auctionID, data['fishID'], data['winnerID'], data['winnerName'], data['currentPrice'], data['timestart'], data['status'], data['timeEnd'], data['itemName'])

    try:
        db.session.add(auction)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify(
            {
                "code": 500,
                "data": {
                    "auctionID": auctionID
                },
                "message": "An error occurred creating the auction item."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": {
                "auctionID": auction.auctionID, "fishID": auction.fishID,
                "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                "status": auction.status
            }
        }
    ), 201

@app.route("/auction/end", methods=['PUT'])
def end_auction():
    with app.app_context():

        data = request.get_json()
        print(data)
        try:
            result = []
            for auction in data:
                auction_item = db.session.query(Auction).get(auction["auctionID"])
                auction_item.timeEnd, auction["timeEnd"] = datetime.now(timezone.utc), datetime.now(timezone.utc).isoformat()
                auction_item.status, auction["status"] = "Ended", "Ended"
                db.session.commit()
                result.append(auction_item)

            # emit_update(data)
            emit_update(json.dumps(data, default=str))
            return jsonify(
                {
                    "code": 200,
                    "data": {
                    "auction": [{"auctionID": auction.auctionID, "fishID": auction.fishID,
                                    "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                                    "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                                    "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                                    "status": auction.status} 
                                    for auction in result]
                        }
                }
            ), 200
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "message": "An error occurred while updating the auction. " + str(e)
                    },
                }
            ), 500


@app.route("/auction/reset", methods=['PUT'])
def reset_auction():
    with app.app_context():
        data = request.get_json()
        print(data)
        try:
            result = []
            for auction in data:
                auction_item = db.session.query(Auction).get(auction["auctionID"])
                auction_item.timestart, auction["timestart"] = datetime.now(timezone.utc), datetime.now(timezone.utc).isoformat()
                auction_item.timeEnd, auction["timeEnd"] = (datetime.now(timezone.utc) + timedelta(minutes=5)), (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
                auction_item.status, auction["status"] = "Active", "Active"
                auction_item.orderID, auction["orderID"] = "", ""
                auction_item.winnerID, auction["winnerID"] = '1', '1'
                auction_item.winnerName, auction["winnerName"] = "John Doe", "John Doe"
                auction_item.currentPrice, auction["currentPrice"] = "20", "20"

                db.session.commit()
                result.append(auction_item)

            emit_update(json.dumps(data, default=str))
            return jsonify(
                {
                    "code": 200,
                    "data": {
                    "auction": [{"auctionID": auction.auctionID, "fishID": auction.fishID,
                                    "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                                    "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                                    "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                                    "status": auction.status} 
                                    for auction in result]
                        }
                }
            ), 200
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "message": "An error occurred while updating the auction. " + str(e)
                    },
                }
            ), 500

@app.route("/auction/updateOrder/<int:auctionID>", methods=['PUT'])
def update_order_auction(auctionID):
    data = request.get_json()
    print(data)
    try:
        auction = db.session.query(Auction).get(auctionID)
        auction.orderID = data["orderID"]
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "data": {
                "auction": {"auctionID": auction.auctionID, "fishID": auction.fishID,
                                "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                                "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                                "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                                "status": auction.status} 
                    }
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "message": "An error occurred while updating the auction. " + str(e)
                },
            }
        ), 500

@app.route("/auction/<int:auctionID>", methods=['PUT'])
def update_auction(auctionID):
    try:
        auction = db.session.query(Auction).get(auctionID)
        if not auction:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "auctionID": auctionID
                    },
                    "message": "auction not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data:
            if float(data['currentPrice']) > float(auction.currentPrice):
                auction.currentPrice = data['currentPrice']
                auction.winnerID = data['winnerID']
                auction.winnerName = data['winnerName']

                db.session.commit()
                emit_update(data)
                return jsonify(
                    {
                        "code": 200,
                        "data": {
                            "auctionID": auction.auctionID, "fishID": auction.fishID,
                            "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                            "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                            "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                            "status": auction.status
                            }
                    }
                ), 200
            else:
                auction.currentPrice = data['currentPrice']
                auction.winnerID = data['winnerID']
                auction.winnerName = data['winnerName']

                db.session.commit()
                emit_update(data)
                return jsonify(
                    {
                        "code": 200,
                        "data": {
                            "auctionID": auction.auctionID, "fishID": auction.fishID,
                            "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                            "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                            "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                            "status": auction.status
                            }
                    }
                ), 200
                return jsonify(
                    {
                        "code": 500,
                        "message": "Bid placed is lower or equal to current bid."
                    }
                ), 500
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

# @app.route('/')
# def index():
#     return 'Flask-SocketIO Server'

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Emit real-time updates to the connected clients
def emit_update(data):
    with app.app_context():
        socketio.emit('update', data)

def receiveAuctionBid(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=a_queue_name, on_message_callback=callback, auto_ack=True)
        print('Auction_Bid: Consuming from queue:', a_queue_name)
        thread = Thread(target = channel.start_consuming)
        thread.start()  # an implicit loop waiting to receive messages;
             #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
        websocket_thread = Thread(target=emit_update)
        websocket_thread.start()
    
    except pika.exceptions.AMQPError as e:
        print(f"Auction_Bid: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("Auction_Bid: Program interrupted by user.") 

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nauction_bid: Received an auction bid by " + __file__)
    response = processBid(json.loads(body))

    # Publish the response back to the reply queue
    channel.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=response[0].data
    )
    print()

def processBid(auctionInfo):
    with app.app_context():
        try:
            data = auctionInfo
            auction = db.session.query(Auction).get(data['auctionID'])
            
            if not auction:
                return jsonify(
                    {
                        "code": 404,
                        "data": {
                            "auctionID": data['auctionID']
                        },
                        "message": "auction not found."
                    }
                ), 404

            # update status
            # data = request.get_json()


            if data:
                if float(data['currentPrice']) > float(auction.currentPrice):
                    auction.currentPrice = data['currentPrice']
                    auction.winnerID = data['winnerID']
                    auction.winnerName = data['winnerName']

                    db.session.commit()
                    
                    # emit_update(data)
                    return jsonify(
                        {
                            "code": 200,
                            "data": {
                                "auctionID": auction.auctionID, "fishID": auction.fishID,
                                "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                                "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                                "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                                "status": auction.status
                                }
                        }
                    ), 200
                else:
                    # auction.currentPrice = data['currentPrice']
                    # auction.winnerID = data['winnerID']
                    # auction.winnerName = data['winnerName']

                    # db.session.commit()
                    # emit_update(data)

                    # return jsonify(
                    #     {
                    #         "code": 200,
                    #         "data": {
                    #             "auctionID": auction.auctionID, "fishID": auction.fishID,
                    #             "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                    #             "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                    #             "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                    #             "status": auction.status
                    #             }
                    #     }
                    # ), 200
                    return jsonify(
                        {
                            "code": 500,
                            "message": "Bid placed is lower or equal to current bid."
                        }
                    ), 500
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "auctionID": data['auctionID'],
                    },
                    "message": "An error occurred while updating the auction. " + str(e)
                }
            ), 500
        
@app.route("/auction/bidding/<int:auctionID>", methods=["PUT"])
def update_bidder_auction(auctionID):
    auction = Auction.query.get(auctionID)

    if not auction:
        return jsonify({"code": 404, "message": "Order not found."}), 404

    data = request.get_json()

    auction.winnerID = data["bidderID"]
    auction.winnerName = data["bidderName"]
    auction.currentPrice = data["biddingPrice"]


    db.session.commit()

    return (
        jsonify(
            {"code": 200, "data": {
                                "auctionID": auction.auctionID, "fishID": auction.fishID,
                                "winnerID": auction.winnerID, "winnerName": auction.winnerName,
                                "itemName": auction.itemName, "timeEnd": auction.timeEnd,
                                "currentPrice": auction.currentPrice, "timestart": auction.timestart,
                                "status": auction.status
                                }}
        ),
        200,
    )
    
print("Auction_Bid: Getting Connection")
connection = amqp_connection.create_connection() #get the connection to the broker
print("Auction_Bid: Connection established successfully")
channel = connection.channel()
receiveAuctionBid(channel)

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5007, debug=True)




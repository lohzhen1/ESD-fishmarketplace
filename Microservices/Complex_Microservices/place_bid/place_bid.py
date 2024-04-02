from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

from invokes import invoke_http
from flask_socketio import SocketIO, emit

import pika
import json
import amqp_connection

from uuid import uuid4

app = Flask(__name__)
CORS(app)

# Initialize Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins='*')

exchangename = "auction_topic" # exchange name
exchangetype="topic" # use a 'topic' exchange to enable interaction

connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

@app.route("/place_bid", methods=['POST'])
def place_bid():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            bid = request.get_json()
            print("\nReceived an bid in JSON:", bid)

            result = processBid(bid)
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


def processBid(bid):

    print('\n\n-----Publishing the (bid info) message with routing_key=bid.auction-----')        

    message = json.dumps(bid)
    # Generate a unique correlation ID
    correlation_id = str(uuid4())

    # Create a queue for receiving the reply
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    reply = 500

    # Define the response callback function
    def on_response(ch, method, props, body):
        if props.correlation_id == correlation_id:
            response = body.decode()
            response = json.loads(response)

            nonlocal reply 
            reply = response['code']

            # Use the response as desired
            # e.g., return the response to the client
            msg = json.dumps(response['data'])
            if reply == 200:
                emit_update(response['data'])
                channel.basic_publish(exchange=exchangename, routing_key="bid.record", body=msg)
    
                print("\nRecord bid placed.\n")
            channel.stop_consuming()


    # Set up the consumer for the response
    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )

    # invoke_http(activity_log_URL, method="POST", json=bid_result)            
    channel.basic_publish(exchange=exchangename, routing_key="bid.auction", 
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=correlation_id,
        ),body=message)
    
    # Start consuming messages to receive the response
    channel.start_consuming()

    print("\nAuction update.\n")       
    
    if reply != 500:

        return {
            "code": 201,
            "message": 'Bid success'
        }
    else:
        return {
            "code": 500,
            "message": "Bid failed."
        }

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Emit real-time updates to the connected clients
def emit_update(data):
    socketio.emit('update', data)

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an bid...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

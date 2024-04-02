from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os, sys
import logging

import requests

import pika
import json

from uuid import uuid4

app = Flask(__name__)
CORS(app)

# This is to run from azure database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.route("/retrieve_cart_items/<int:userID>", methods=["GET"])
def get_cart_item(userID):
    # Validate userID
    if userID is None or userID <= 0:
        logging.error("Invalid userID: %s", userID)
        return jsonify({"message": "Invalid userID"}), 400

    # Log the received userID
    logging.info("Received userID: %s", userID)

    cartID = get_cartID(userID)
    logging.info("Retrieved cartID: %s for userID: %s", cartID, userID)

    if cartID is None:
        logging.error("No cart found for userID: %s", userID)
        return jsonify({"message": "No cart found for this user"}), 404
    else:
        # Query cart_items for cartID
        cart_items = get_cart_item_with_cartID(cartID)
        logging.info(
            "Retrieved cart items: %s for cartID: %s", cart_items, cartID
        )  # Log the retrieved cart items
        return cart_items


def get_cartID(userID):
    """
    Retrieves the cart ID for a given user ID.

    Args:
        userID (int): The ID of the user.

    Returns:
        str: The cart ID associated with the user, or None if an error occurs.
    """
    try:
        # Query cart for cartID using userID
        userID = int(userID)
        response = requests.get(f"http://cart:5004/cart/{userID}")

        # Check the response status code
        if response.status_code != 200:
            logging.error(
                "Error getting cart ID, status code: %s", response.status_code
            )
            return None

        # Parse the response data as JSON
        data = response.json()
        logging.info("Response data: %s", data)

        # Extract the cartID from the response data
        cartID = data.get("data").get("cartID")

        return cartID

    except requests.exceptions.RequestException as e:
        logging.error("Request error: %s", e)
        return None

    except Exception as e:
        logging.error("Error getting cart ID: %s", e)
        return None


def get_cart_item_with_cartID(cartID):
    # Validate cartID
    try:
        cartID = int(cartID)
        if cartID <= 0:
            logging.error("Invalid cartID: %s", cartID)
            return jsonify({"message": "Invalid cartID"}), 400
    except ValueError:
        logging.error("Invalid cartID: %s", cartID)
        return jsonify({"message": "Invalid cartID"}), 400

    # Query cart_items for cartID
    response = requests.get(f"http://cart-item:5062/cart_items/{cartID}")

    # Check the response status code
    if response.status_code != 200:
        logging.error("Error getting cart items, status code: %s", response.status_code)
        return jsonify({"message": "Error getting cart items"}), 500

    # Parse the response data as JSON
    cart_items = response.json()
    logging.info("Retrieved cart items: %s for cartID: %s", cart_items, cartID)

    return jsonify(cart_items)


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5105, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

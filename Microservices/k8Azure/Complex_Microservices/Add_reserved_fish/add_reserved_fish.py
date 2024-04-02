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


@app.route("/add_reserved_fish", methods=["POST"])
def add_reserved_fish():
    """
    Add reserved fish to the cart and delete the reservation.

    This function receives a JSON payload containing the necessary information
    to add a reserved fish to the cart and delete the corresponding reservation.
    The required fields in the JSON payload are 'fishID', 'itemName', 'price',
    'qty', 'cartID', and 'reserveID'.

    Returns:
        A JSON response with a success message if the reserved fish is
        successfully added to the cart and the reservation is deleted.
        Otherwise, returns an error message with an appropriate status code.
    """
    try:
        data = request.get_json()
        logging.info("Received data: %s", data)

        # Extract the required fields
        fishID = data.get("fishID")
        itemName = data.get("itemName")
        price = data.get("price")
        qty = data.get("qty")
        cartID = data.get("cartID")
        reserveID = data.get("reserveID")

        # Add reserved fish to cart
        addToCart = add_reserved_fish_to_cart(fishID, itemName, price, qty, cartID)

        # Check the response code
        if addToCart != 201:
            return jsonify({"message": "Failed to add reserved fish to cart"}), 400

        # Delete the Reservation
        check_remove = remove_reservation(reserveID)
        if check_remove != 200:
            return jsonify({"message": "Failed to delete reservation"}), 400
        return (
            jsonify(
                {
                    "message": "Successfully added reserved fish to cart & removed from reservation"
                }
            ),
            201,
        )

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        return jsonify({"message": "An error occurred"}), 500


def add_reserved_fish_to_cart(fishID, itemName, price, qty, cartID):
    """
    Add reserved fish to the cart.

    Args:
        fishID (int): The ID of the reserved fish.
        itemName (str): The name of the reserved fish item.
        price (float): The price of the reserved fish.
        qty (int): The quantity of the reserved fish.
        cartID (int): The ID of the cart to add the reserved fish to.

    Returns:
        int: The status code of the operation. 201 if successful, 400 otherwise.
    """
    try:
        data = {
            "fishID": fishID,
            "itemName": itemName,
            "price": price,
            "qty": qty,
        }

        # Send a POST request to the add_fish_to_cart endpoint
        response = requests.post(
            f"http://cart-item:5062/cart_items/{cartID}/add_fish",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )

        # Check the response
        if response.status_code == 201:
            print("Successfully added reserved fish to cart")
            return 201
        else:
            print("Failed to add reserved fish to cart")
            return 400

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        return 400


def remove_reservation(reserveID):
    """
    Removes a reservation by sending a DELETE request to the delete_reservation endpoint.

    Args:
        reserveID (int): The ID of the reservation to be deleted.

    Returns:
        int: The status code of the request. Returns 200 if the reservation was successfully deleted,
             and 400 if there was an error or the reservation could not be deleted.
    """
    try:
        # Send a DELETE request to the delete_reservation endpoint
        response = requests.delete(
            f"http://reservation:5003/reservation/delete/{reserveID}"
        )

        # Check the response
        if response.status_code == 200:
            print("Successfully deleted reservation")
            return 200
        else:
            print("Failed to delete reservation")
            return 400

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        return 400


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5125, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

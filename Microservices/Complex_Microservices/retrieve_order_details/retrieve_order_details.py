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


@app.route("/retrieve_order_details/<int:userID>", methods=["GET"])
def get_order_detail(userID):
    """
    Retrieve order details for a given user ID and return the details as JSON response.

    Parameters:
    - userID: An integer representing the user ID

    Returns:
    - JSON response containing the order details or an error message and status code
    """
    # Validate userID
    if userID is None or userID <= 0:
        logging.error("Invalid userID: %s", userID)
        return jsonify({"message": "Invalid userID"}), 400

    # Log the received userID
    logging.info("Received userID: %s", userID)

    # Retrieve orders for the given userID
    orders = get_order_today(userID)

    # Check if any orders were retrieved
    if orders is None:
        logging.error("No order retrieved for userID: %s", userID)
        return jsonify({"message": "No order found for this userID"}), 404
    else:
        logging.info("Retrieved orders: %s for userID: %s", orders, userID)
        order_details_list = []

        # Iterate over each order and fetch order details
        for order in orders:
            orderID = order.get("orderID")
            if orderID is not None:
                order_details = fetch_order_details(orderID)
                if order_details is not None:
                    order_details_list.append(order_details)

        # Flatten the order details list
        flat_order_details_list = [
            item for sublist in order_details_list for item in sublist
        ]

        logging.info(
            "Retrieved order details: %s for userID: %s",
            flat_order_details_list,
            userID,
        )

        return jsonify(flat_order_details_list), 200


def get_order_today(userID):
    """
    Retrieves the orders for the specified user for the current day.

    Args:
        userID (int): The ID of the user for whom the orders are to be retrieved.

    Returns:
        list: A list of orders for the specified user for the current day. Returns None if there is an error.
    """
    try:
        userID = int(userID)  # Convert the userID to an integer
        url = f"http://order:5009/orders/today/{userID}"  # Construct the URL for the API endpoint
        logging.debug("Request URL: %s", url)  # Log the URL for debugging purposes
        response = requests.get(url)  # Send a GET request to the API endpoint

        if (
            response.status_code != 200
        ):  # Check if the response status code is not 200 (indicating an error)
            logging.error(
                "Error getting order today, status code: %s, response: %s",
                response.status_code,
                response.text,
            )
            return None  # Return None to indicate an error
        else:
            response_data = response.json()  # Parse the response JSON data
            orders = response_data.get("data", {}).get(
                "orders", []
            )  # Extract the orders from the response data
            return orders  # Return the list of orders
    except (
        Exception
    ) as e:  # Catch any exceptions that occur during the execution of the code
        logging.error("Error getting order today: %s", e)
        return None  # Return None to indicate an error


def fetch_order_details(orderID):
    """
    Fetches order details for a given orderID and returns a list of fishIDs.

    Parameters:
    - orderID: A string representing the order ID

    Returns:
    - A list of fishIDs for the specified order
    """
    try:
        url = f"http://order_details:5050/order/details/{orderID}"
        logging.debug("Request URL for order details: %s", url)
        response = requests.get(url)

        if response.status_code != 200:
            logging.error(
                "Error getting order details, status code: %s, response: %s",
                response.status_code,
                response.text,
            )
            return []
        else:
            response_data = response.json()
            fishIDs = response_data.get("data", {}).get("fishIDs", [])
            order_details = []

            for fishID in fishIDs:
                if fishID not in order_details:
                    order_details.append(fishID)

            logging.info("Fish IDs for the specified order: %s", order_details)
            return order_details
    except Exception as e:
        logging.error("Error getting order details: %s", e)
        return []


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5110, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

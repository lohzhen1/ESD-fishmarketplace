from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

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


@app.route("/handle_reservation_payment", methods=["POST"])
def handle_reservation_payment():
    """
    Handle reservation payment.

    This function handles the reservation payment by performing the following steps:
    1. Retrieve the JSON data from the request.
    2. Validate the total price.
    3. Perform Stripe payment.
    4. Create an order.
    5. Create order details.

    Returns:
        A JSON response indicating the status of the reservation payment handling.

    Raises:
        None
    """
    data = request.get_json()
    logging.info("Received data: %s", data)
    totalPrice = data.get("total_price")

    # Validate totalPrice
    if not validate_total_price(totalPrice):
        return jsonify({"message": "Invalid totalPrice"}), 400
    # Log the received totalPrice
    logging.info("Received totalPrice: %s", totalPrice)

    # Perform Order Creation
    order_response = handle_order_creation(data)
    if order_response is None:
        return jsonify({"message": "Failed to create order"}), 500

    cartItems = data.get("cartItems")
    orderID = order_response["data"]["orderID"]
    logging.info("CartItems: %s", cartItems)

    order_details_response, status_code = handle_order_details_creation(
        cartItems, orderID
    )
    if status_code != 200:
        logging.error(f"Failed to create order details: {order_details_response}")
        return order_details_response, status_code

    logging.info("Created order details: %s", order_details_response)

    # Delete all Cart Items belonging to cartID
    cartID = data.get("cartID")
    delete_cart_items(cartID)

    # Remove the quantity from Inventory
    return jsonify({"message": "Reservation payment handled successfully"}), 200


# Delete Cart Items
def delete_cart_items(cartID):
    # Extract the cartID from the cartItem

    # Define the URL of the delete_cart endpoint
    url = f"http://cart-item:5062/cart_items/delete/{cartID}"

    # Make the HTTP DELETE request
    response = requests.delete(url)

    # Check the status code of the response
    if response.status_code != 200:
        logging.error(f"Failed to delete cart items: {response.content}")
        return None

    logging.info("Deleted cart items successfully")
    return response.json()


# Create Order
def handle_order_creation(data):
    """
    A function to handle the creation of an order.

    Parameters:
    - data: The data containing information about the order.

    Returns:
    - If successful, returns the JSON response from the create_order endpoint. If unsuccessful, returns None.
    """
    # Define the URL of the create_order endpoint
    url = "http://order:5009/order"

    # Define the data to be sent in the POST request
    order_data = {
        "userID": data.get("userID"),
        "orderedTime": datetime.now(timezone.utc).isoformat(),
        "paymentMethod": "Stripe",
        "deliveryAddress": data.get("deliveryAddress"),
        "totalPrice": data.get("total_price"),
        "status": "Completed",
        "supplierID": 3,
        "supplierName": "Ah Tan Pte Ltd",
        "checkoutID": data.get("checkoutID"),
    }

    logging.info("Create order_data: %s", order_data)

    # Make the POST request and get the response
    response_data = requests.post(url, json=order_data)
    response_json = response_data.json()

    logging.info(f"Response data, Order Creation: {response_json}")

    if "code" in response_json and response_json["code"] == 201:
        return response_json
    else:
        print("Error: Failed to create order.")
        return None


def handle_order_details_creation(cartItems, orderID):
    """
    Ensures that every order_detail is created,  else throw an error

    Args:
        cartItems (list): A list of items in the cart.
        orderID (int): The ID of the order.

    Returns:
        tuple: A tuple containing the response message and status code.
    """
    # Counter to check if all order_details are created successfully
    counter = 0
    for item in cartItems:
        order_detail_data = {
            "orderID": orderID,
            "fishID": item["fishID"],
            "qty": item["qty"],
            "subTotal": item["qty"] * item["price"],
            "itemName": item["itemName"],
        }
        # Perform creation of order_details
        order_details = create_order_details(order_detail_data)
        logging.info(f"Order details response: {order_details}")

        # Do counting if all order_details are created successfully
        if "code" in order_details and order_details["code"] == 201:
            counter += 1

    if counter == len(cartItems):
        return jsonify({"message": "All order_details created successfully"}), 200
    else:
        return jsonify({"message": "Not all cartItems are created successfully"}), 400


# Create Order_Details
def create_order_details(order_detail_data):
    """
    Creates order details based on the provided order detail data.

    Args:
        order_detail_data (dict): The data for creating the order details.

    Returns:
        dict or None: The response JSON containing the created order details if successful,
        None otherwise.
    """
    # Calling the create_order_details endpoint
    url = "http://order-details:5050/order/details"
    response = requests.post(url, json=order_detail_data)
    response_json = response.json()

    if (
        response_json
        and "orderID" in response_json["data"]
        and response_json["code"] == 201
    ):
        return response_json
    else:
        print("Error: Failed to create order_detail.")
        return None


def validate_total_price(totalPrice):
    if totalPrice is None or totalPrice <= 0:
        logging.error("Invalid totalPrice: %s", totalPrice)
        return False
    return True


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5090, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import ForeignKey
import logging


app = Flask(__name__)
CORS(app)

##to run locally (assuming you have phpmyadmin table all set up)
##app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/cart'


# This is to run from azure database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Cart(db.Model):

    # this is azure sql server table
    __tablename__ = "Cart"

    cartID = db.Column(db.Integer, primary_key=True)  # Cart ID
    userID = db.Column(db.Integer, ForeignKey("user.userID"), nullable=False)  # User ID

    # Initialize Cart object
    def __init__(self, cartID, userID):
        self.cartID = cartID  # Set cart ID
        self.userID = userID  # Set user ID


class Cart_Item(db.Model):
    __tablename__ = "Cart_Item"
    cartItemID = db.Column(db.Integer, primary_key=True)  # Cart Item ID
    cartID = db.Column(db.Integer, ForeignKey("Cart.cartID"), nullable=False)  # Cart ID
    fishID = db.Column(db.Integer, nullable=False)  # Fish ID
    itemName = db.Column(db.String(100), nullable=False)  # Item Name
    price = db.Column(db.Float, nullable=False)  # Price
    qty = db.Column(db.Integer, nullable=False)  # Quantity

    def __init__(self, cartID, fishID, itemName, price, qty):
        self.cartID = cartID
        self.fishID = fishID
        self.itemName = itemName
        self.price = price
        self.qty = qty


@app.route("/cart_items/<int:cartID>", methods=["GET"])
def get_cart_items(cartID):
    """
    Retrieve the cart items for a given cart.

    Args:
        cartID (int): The ID of the cart.

    Returns:
        A JSON response containing the cart items if found, or an error message if not found.
    """

    if cartID is None:
        logging.error("Missing cartID")
        return jsonify({"error": "Missing cartID"}), 400

    logging.info("Received cartID: %s", cartID)

    logging.info("Querying for cart items with cartID: %s", cartID)
    cart_items = Cart_Item.query.filter_by(cartID=cartID).all()
    logging.info("Retrieved cart items: %s", cart_items)

    if not cart_items:
        logging.error("No items found for cartID: %s", cartID)
        return jsonify({"error": "No items found for this cart"}), 404

    # Convert cart items to a list of dictionaries to be JSON serializable
    cart_items_list = [
        {
            "fishID": item.fishID,
            "itemName": item.itemName,
            "price": item.price,
            "qty": item.qty,
        }
        for item in cart_items
    ]

    for item in cart_items_list:
        logging.info("Retrieved item: %s for cartID: %s", item, cartID)

    return jsonify(cart_items_list), 200


# Method to add a fish to the cart
@app.route("/cart_items/<int:cartID>/add_fish", methods=["POST"])
def add_fish_to_cart(cartID):
    data = request.get_json()
    # Do Logging
    logging.info(
        "Received request to add fish to cart with cartID: %s and data: %s",
        cartID,
        data,
    )

    # Check if the cart item already exists
    cartItem = Cart_Item.query.filter_by(cartID=cartID, fishID=data["fishID"]).first()

    if cartItem:
        # If the cart item exists, update the quantity
        cartItem.qty += data["qty"]
        message = "The quantity of the fish in the cart was updated."
    else:
        # If the cart item doesn't exist, create a new one
        cartItem = Cart_Item(
            cartID,
            data["fishID"],
            data["itemName"],
            data["price"],
            data["qty"],
        )
        db.session.add(cartItem)
        message = "The fish was added to the cart."

    try:
        db.session.commit()
    except Exception as e:
        logging.error("An error occurred while updating the cart: %s", e)
        return (
            jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while updating the cart.",
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "code": 201,
                "message": message,
                "data": {
                    "cartItemID": cartItem.cartItemID,
                    "cartID": cartItem.cartID,
                    "fishID": cartItem.fishID,
                    "itemName": cartItem.itemName,
                    "price": cartItem.price,
                    "qty": cartItem.qty,
                },
            }
        ),
        201,
    )


@app.route("/cart_items/delete/<int:cartID>", methods=["DELETE"])
def delete_cartItems(cartID):
    # Query for cart items with the given cartID
    cart_items = Cart_Item.query.filter_by(cartID=cartID).all()

    if not cart_items:
        return jsonify({"error": "No items found for this cart"}), 404

    # Delete each item
    for item in cart_items:
        db.session.delete(item)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Cart items deleted successfully"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5062, debug=True)

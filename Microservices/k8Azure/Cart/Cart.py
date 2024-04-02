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


# route to the root directory
@app.route("/")

# method to return the number of cart_records in azure database
def index():
    cart_rec = Cart.query.all()
    return "Number of cart_records: %d" % len(cart_rec)


# Method to return all the carts by using GET method
@app.route("/cart", methods=["GET"])
def get_all_carts():
    cart_list = db.session.query(Cart).all()  # Query all carts

    if len(cart_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "carts": [
                        {"cartID": cart.cartID, "userID": cart.userID}
                        for cart in cart_list
                    ]
                },
            }
        )
    return jsonify({"code": 404, "message": "There are no carts."}), 404


# Method to return the specific cart by using cartID
@app.route("/cart/<int:cartID>", methods=["GET"])
def find_by_cartID(cartID):
    cart = db.session.query(Cart).get(cartID)

    if cart:
        return jsonify(
            {"code": 200, "data": {"cartID": cart.cartID, "userID": cart.userID}}
        )
    return jsonify({"code": 404, "message": "Cart not found."}), 404


# Create Cart by using POST
@app.route("/cart", methods=["POST"])
def create_cart():
    """
    Create a new cart.

    This function handles the POST request to create a new cart. It expects a JSON payload
    containing the cartID and userID. If the cartID already exists in the database, it returns
    a JSON response with a 400 status code and an error message. If the cartID doesn't exist,
    it creates a new cart with the provided cartID and userID, adds it to the database, and
    returns a JSON response with a 201 status code and the created cart's details.

    Returns:
        A JSON response with a status code and data.

    Raises:
        500: If an error occurs while creating the cart.
    """
    data = request.get_json()
    cartID = data["cartID"]
    if db.session.query(Cart).get(cartID):
        return (
            jsonify(
                {
                    "code": 400,
                    "data": {"cartID": cartID},
                    "message": "Cart already exists.",
                }
            ),
            400,
        )

    cart = Cart(cartID, data["userID"])

    try:
        db.session.add(cart)
        db.session.commit()
    except:
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"cartID": cartID},
                    "message": "An error occurred creating the cart.",
                }
            ),
            500,
        )

    return (
        jsonify({"code": 201, "data": {"cartID": cart.cartID, "userID": cart.userID}}),
        201,
    )


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


@app.route("/cart/<int:userID>", methods=["GET"])
def get_cart_id(userID):
    """
    Retrieve the cart ID for a given user.

    Args:
        userID (int): The ID of the user.

    Returns:
        A JSON response containing the cart ID if found, or an error message if not found.
    """

    if userID is None:
        return jsonify({"error": "Missing userID"}), 400

    cart = Cart.query.filter_by(userID=userID).first()

    if cart is None:
        return jsonify({"error": "No cart found for this user"}), 404

    return jsonify({"cartID": cart.cartID}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)

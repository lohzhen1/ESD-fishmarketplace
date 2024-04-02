from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
from sqlalchemy import ForeignKey, func
import logging

app = Flask(__name__)
CORS(app)

##to run locally (assuming you have phpmyadmin table all set up)
##app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/order'

# This is to run from azure database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "User"

    userID = db.Column(db.Integer, primary_key=True)


class Order(db.Model):
    # this is azure sql server table
    __tablename__ = "Order"

    orderID = db.Column(db.Integer, primary_key=True)  # Order ID
    userID = db.Column(db.Integer, ForeignKey("User.userID"), nullable=False)  # User ID
    orderedTime = db.Column(db.DateTime, default=datetime.utcnow)  # Ordered Time
    paymentMethod = db.Column(db.String, nullable=False)  # Payment Method
    deliveryAddress = db.Column(db.String, nullable=False)  # Delivery Address
    totalPrice = db.Column(db.Float, nullable=False)  # Total Price
    status = db.Column(db.String, nullable=False)  # Status
    checkoutID = db.Column(db.String, nullable=False)  # Status

    supplierID = db.Column(
        db.Integer, ForeignKey("User.userID"), nullable=False
    )  # Supplier ID
    supplierName = db.Column(db.String, nullable=False)  # Supplier Name

    # Initialize Order object
    def __init__(
        self,
        # orderID,
        userID,
        orderedTime,
        paymentMethod,
        deliveryAddress,
        totalPrice,
        status,
        supplierID,
        supplierName,
        checkoutID,
    ):
        # self.orderID = orderID  # Set order ID
        self.userID = userID  # Set user ID
        self.orderedTime = orderedTime  # Set ordered time
        self.paymentMethod = paymentMethod  # Set payment method
        self.deliveryAddress = deliveryAddress  # Set delivery address
        self.totalPrice = totalPrice  # Set total price
        self.status = status  # Set status
        self.supplierID = supplierID  # Set supplier ID
        self.supplierName = supplierName  # Set supplier name
        self.checkoutID = checkoutID


# route to the root directory
@app.route("/")

# method to return the number of order_records in azure database
def index():
    order_rec = Order.query.all()
    return "Number of order_records: %d" % len(order_rec)


# Method to return all the orders by using GET method
@app.route("/order", methods=["GET"])
def get_all_orders():
    order_list = db.session.query(Order).all()  # Query all orders

    if len(order_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [
                        {
                            "orderID": order.orderID,
                            "userID": order.userID,
                            "orderedTime": order.orderedTime,
                            "paymentMethod": order.paymentMethod,
                            "deliveryAddress": order.deliveryAddress,
                            "totalPrice": order.totalPrice,
                            "status": order.status,
                            "supplierID": order.supplierID,
                            "supplierName": order.supplierName,
                            "checkoutID": order.checkoutID,
                        }
                        for order in order_list
                    ]
                },
            }
        )
    return jsonify({"code": 404, "message": "There are no orders."}), 404


# Queue
@app.route("/orders/today/<int:userID>", methods=["GET"])
def get_orders_today(userID):
    """
    Retrieve orders placed by a specific user today.

    Args:
        userID (int): The ID of the user.

    Returns:
        A JSON response containing the orders placed by the user today.
        If no orders are found, a JSON response with a 404 status code and a message is returned.
    """
    today = datetime.now().date()
    orders = Order.query.filter(
        db.cast(Order.orderedTime, db.Date) == today, Order.userID == userID
    ).all()

    if orders:
        return jsonify(
            {
                "code": 200,
                "data": {"orders": [{"orderID": order.orderID} for order in orders]},
            }
        )
    return (
        jsonify({"code": 404, "message": "No orders found for today for this user."}),
        404,
    )


# Method to return all orders for a specific user by using userID
@app.route("/order/user/<int:userID>", methods=["GET"])
def get_orders_by_user(userID):
    order_list = (
        db.session.query(Order).filter(Order.userID == userID).all()
    )  # Query orders by userID

    if len(order_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [
                        {
                            "orderID": order.orderID,
                            "userID": order.userID,
                            "orderedTime": order.orderedTime,
                            "paymentMethod": order.paymentMethod,
                            "deliveryAddress": order.deliveryAddress,
                            "totalPrice": order.totalPrice,
                            "status": order.status,
                            "supplierID": order.supplierID,
                            "supplierName": order.supplierName,
                            "checkoutID": order.checkoutID,
                        }
                        for order in order_list
                    ]
                },
            }
        )
    return jsonify({"code": 404, "message": "No orders found for this user."}), 404


# Method to return the specific order by using orderID
@app.route("/order/<int:orderID>", methods=["GET"])
def find_by_orderID(orderID):
    order = db.session.query(Order).get(orderID)

    if order:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orderID": order.orderID,
                    "userID": order.userID,
                    "orderedTime": order.orderedTime,
                    "paymentMethod": order.paymentMethod,
                    "deliveryAddress": order.deliveryAddress,
                    "totalPrice": order.totalPrice,
                    "status": order.status,
                    "supplierID": order.supplierID,
                    "supplierName": order.supplierName,
                    "checkoutID": order.checkoutID,
                },
            }
        )
    return jsonify({"code": 404, "message": "Order not found."}), 404


@app.route("/order", methods=["POST"])
def create_order():
    data = request.get_json()
    # OrderID is now auto generated
    # orderID = data["orderID"]
    # if db.session.query(Order).get(orderID):
    #     return (
    #         jsonify(
    #             {
    #                 "code": 400,
    #                 "data": {"orderID": orderID},
    #                 "message": "Order already exists.",
    #             }
    #         ),
    #         400,
    #     )

    # Convert the ISO 8601 string to a datetime object
    orderedTime = datetime.fromisoformat(data["orderedTime"])

    # Convert the datetime object to the format that SQL Server expects
    orderedTime = orderedTime.strftime("%Y-%m-%d %H:%M:%S")

    # Use the formatted orderedTime in your Order object
    order = Order(
        data["userID"],
        orderedTime,
        data["paymentMethod"],
        data["deliveryAddress"],
        data["totalPrice"],
        data["status"],
        data["supplierID"],
        data["supplierName"],
        data["checkoutID"],
    )

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        logging.error("An error occurred creating the order: %s", e)
        return (
            jsonify(
                {
                    "code": 500,
                    "message": "An error occurred creating the order.",
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "code": 201,
                "data": {
                    "orderID": order.orderID,
                    "userID": order.userID,
                    "orderedTime": order.orderedTime,
                    "paymentMethod": order.paymentMethod,
                    "deliveryAddress": order.deliveryAddress,
                    "totalPrice": order.totalPrice,
                    "status": order.status,
                    "supplierID": order.supplierID,
                    "supplierName": order.supplierName,
                    "checkoutID": order.checkoutID,
                },
            }
        ),
        201,
    )

    # Method to update an order status by using PUT method


@app.route("/order/<int:order_id>", methods=["PUT"])
def update_order_status(order_id):
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"code": 404, "message": "Order not found."}), 404

    data = request.get_json()

    if "status" in data:
        order.status = data["status"]

    db.session.commit()

    return (
        jsonify(
            {"code": 200, "data": {"orderID": order.orderID, "status": order.status}}
        ),
        200,
    )


@app.route("/order/info/<int:order_id>", methods=["PUT"])
def update_order_info(order_id):
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"code": 404, "message": "Order not found."}), 404

    data = request.get_json()

    order.status = data["status"]
    order.paymentMethod = data["paymentMethod"]
    order.checkoutID = data["checkoutID"]
    order.deliveryAddress = data["deliveryAddress"]

    db.session.commit()

    return (
        jsonify(
            {"code": 200, "data": {"orderID": order.orderID, "status": order.status}}
        ),
        200,
    )

@app.route("/order/user/<int:order_id>", methods=["PUT"])
def update_order_user(order_id):
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"code": 404, "message": "Order not found."}), 404

    data = request.get_json()

    order.userID = data["userID"]

    db.session.commit()

    return (
        jsonify(
            {"code": 200, "data": {"orderID": order.orderID}}
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009, debug=True)

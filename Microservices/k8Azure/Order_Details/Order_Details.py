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
    supplierID = db.Column(
        db.Integer, ForeignKey("User.userID"), nullable=False
    )  # Supplier ID
    supplierName = db.Column(db.String, nullable=False)  # Supplier Name


class OrderDetail(db.Model):
    # Azure SQL Table
    __tablename__ = "Order_Details"

    detailID = db.Column(db.Integer, primary_key=True)
    orderID = db.Column(db.Integer)
    fishID = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    itemName = db.Column(db.Integer)
    subTotal = db.Column(db.Float)
    itemName = db.Column(db.String(100))

    # initialize OrderDetail object
    def __init__(self, orderID, fishID, qty, subTotal, itemName):
        # self.detailID = detailID
        self.orderID = orderID
        self.fishID = fishID
        self.itemName = itemName
        self.qty = qty
        self.subTotal = subTotal
        self.itemName = itemName


@app.route("/order/details/<int:orderID>", methods=["GET"])
def get_order_details(orderID):
    """
    Retrieve the details of an order based on the given order ID.

    Parameters:
    orderID (int): The ID of the order.

    Returns:
    If details are found for the order, returns a JSON response with status code 200 and the fish IDs associated with the order.
    If no details are found for the order, returns a JSON response with status code 404 and an error message.
    """
    details = OrderDetail.query.filter_by(orderID=orderID).all()

    if details:
        return jsonify(
            {
                "code": 200,
                "data": {"fishIDs": [detail.fishID for detail in details]},
            }
        )
    else:
        return (
            jsonify({"code": 404, "message": "No details found for this order."}),
            404,
        )


@app.route("/order/allDetails/<int:orderID>", methods=["GET"])
def get_all_order_details(orderID):
    """
    Retrieve the details of an order based on the given order ID.

    Parameters:
    orderID (int): The ID of the order.

    Returns:
    If details are found for the order, returns a JSON response with status code 200 and the fish IDs associated with the order.
    If no details are found for the order, returns a JSON response with status code 404 and an error message.
    """
    details = OrderDetail.query.filter(OrderDetail.orderID==orderID).all()

    if details:
        return jsonify(
            {
                "code": 200,
                "data": [{"fishIDs": detail.fishID,  "detailID": detail.detailID, "orderID": detail.orderID,
                          "qty": detail.qty,  "subTotal": detail.subTotal, "itemName": detail.itemName }
                          for detail in details],

            }
        )
    else:
        return (
            jsonify({"code": 404, "message": "No details found for this order."}),
            404,
        )


@app.route("/order/details", methods=["POST"])
def create_order_details():
    """
    Create a new order detail.

    This function receives a JSON payload containing the details of a new order detail.
    It creates a new OrderDetail object and adds it to the database.
    If successful, it returns a JSON response with the created order detail's information.
    If an error occurs, it returns a JSON response with an error message.

    Returns:
        A JSON response with the created order detail's information or an error message.

    Raises:
        None
    """
    data = request.get_json()
    logging.info("Received data: %s", data)

    order_detail = OrderDetail(
        data["orderID"],
        data["fishID"],
        data["qty"],
        data["subTotal"],
        data["itemName"],
    )

    try:
        db.session.add(order_detail)
        db.session.commit()
        logging.info("Created order_detail: %s", order_detail)
    except Exception as e:
        logging.error("An error occurred creating the order_detail: %s", e)
        return (
            jsonify(
                {
                    "code": 500,
                    "message": "An error occurred creating the order_detail.",
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "code": 201,
                "data": {
                    "detailID": order_detail.detailID,
                    "orderID": order_detail.orderID,
                    "fishID": order_detail.fishID,
                    "qty": order_detail.qty,
                    "subTotal": order_detail.subTotal,
                    "itemName": order_detail.itemName,
                },
            }
        ),
        201,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

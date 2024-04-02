from uuid import uuid4
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
import urllib
from sqlalchemy import create_engine
import logging

app = Flask(__name__)
CORS(app)

# This is to run from azure database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

##To run locally (assuming you have phpmyadmin table all set up)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/auction'


db = SQLAlchemy(app)


class Reservation(db.Model):
    # this is azure sql server table
    __tablename__ = "Reservation"
    reserveID = db.Column(db.Integer, primary_key=True)  # Reservation ID
    userID = db.Column(db.Integer, ForeignKey("User.userID"), nullable=False)  # User ID
    fishID = db.Column(
        db.Integer, ForeignKey("Inventory.fishID"), nullable=False
    )  # Fish ID
    reserve_timestamp = db.Column(db.DateTime)  # Reservation timestamp

    # Initialize Reservation object
    def __init__(self, userID, fishID):
        self.userID = userID
        self.fishID = fishID
        self.reserve_timestamp = datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "User"

    userID = db.Column(db.Integer, primary_key=True)


class Inventory(db.Model):
    __tablename__ = "Inventory"

    fishID = db.Column(db.Integer, primary_key=True)


# route to the root directory
@app.route("/")


# method to return the number of reservation_records in azure database
def index():
    reservations = Reservation.query.all()
    return "Number of reservations: %d" % len(reservations)


@app.route("/reservation/<int:userID>", methods=["GET"])
def return_by_userID(userID):
    """
    This function returns a list of reservations for a given userID.
    Parameters:
    - userID: int, the ID of the user for whom reservations are to be returned.
    Return:
    - JSON object containing a list of reservations, each with reserveID, userID, fishID, and reserve_timestamp.
    """
    reservation_list = db.session.query(Reservation).filter_by(userID=userID).all()
    if len(reservation_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "reservations": [
                        {
                            "reserveID": reservation.reserveID,
                            "userID": reservation.userID,
                            "fishID": reservation.fishID,
                            "reserve_timestamp": reservation.reserve_timestamp,
                        }
                        for reservation in reservation_list
                    ]
                },
            }
        )


# Method to return all the reservations by using GET method
@app.route("/reservation", methods=["GET"])
def get_all_reservations():
    """
    Get all reservations from the database and return them as a JSON response.
    """
    reservation_list = db.session.query(Reservation).all()  # Query all reservations

    if len(reservation_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "reservations": [
                        {
                            "reserveID": reservation.reserveID,
                            "userID": reservation.userID,
                            "fishID": reservation.fishID,
                            "reserve_timestamp": reservation.reserve_timestamp,
                        }
                        for reservation in reservation_list
                    ]
                },
            }
        )
    return jsonify({"code": 404, "message": "There are no reservations."}), 404


# Method to return the specific reservation by using reserveID
@app.route("/reservation/<int:reserveID>", methods=["GET"])
def find_by_reserveID(reserveID):
    """
    Find a reservation by its ID and return the reservation details in JSON format.

    Parameters:
    reserveID (int): The ID of the reservation to look up.

    Returns:
    json: A JSON object containing the reservation details if found, or a JSON object with an error message and status code 404 if the reservation is not found.
    """
    reservation = db.session.query(Reservation).get(reserveID)

    if reservation:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "reserveID": reservation.reserveID,
                    "userID": reservation.userID,
                    "fishID": reservation.fishID,
                    "reserve_timestamp": reservation.reserve_timestamp,
                },
            }
        )
    else:
        return jsonify({"code": 404, "message": "Reservation not found."}), 404


@app.route("/reservation/create", methods=["POST"])
def create_reservation():
    """
    A function to handle the creation of a reservation.
    Parses the request data, validates it, creates a new Reservation object,
    adds it to the database, and returns a success or error message.

    Returns:
        A JSON response containing a success or error message.

    Raises:
        400 Bad Request: If the request data is missing fishID or userID.
        500 Internal Server Error: If there is an error creating the reservation.

    """
    data = request.get_json()

    # Validate the data
    if "fishID" not in data or "userID" not in data:
        return jsonify({"message": "Missing fishID or userID"}), 400

    fishID = data["fishID"]
    userID = data["userID"]

    try:
        # Create a new Reservation
        reservation = Reservation(userID=userID, fishID=fishID)

        # Add the new Reservation to the database
        db.session.add(reservation)
        db.session.commit()

        return jsonify({"message": "Reservation created"}), 201

    except Exception as e:
        # Log the error
        logging.error("Error creating reservation: %s", e)

        return jsonify({"message": "Error creating reservation"}), 500


@app.route("/reservation/delete/<int:reserveID>", methods=["DELETE"])
def delete_reservation(reserveID):
    # Log the received reserveID
    logging.info("Received reserveID: %s", reserveID)

    try:
        # Find the reservation with the given reserveID
        reservation = Reservation.query.filter_by(reserveID=reserveID).first()

        # If the reservation doesn't exist, return an error
        if not reservation:
            return jsonify({"message": "Reservation not found"}), 404

        # Delete the reservation
        db.session.delete(reservation)
        db.session.commit()

        return jsonify({"message": "Reservation deleted"}), 200

    except Exception as e:
        # Log the error
        logging.error("Error deleting reservation: %s", e)

        return jsonify({"message": "Error deleting reservation"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)

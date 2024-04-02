from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import ForeignKey
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from uuid import uuid4
import base64
from twilio.rest import Client
import pika
import threading
import os







app = Flask(__name__)
CORS(app)



#This is to run from azure database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## pip install azure-storage-blob to install the azure storage blob package
## connection string to connect azure storage account
connec_string= "DefaultEndpointsProtocol=https;AccountName=esdimage;AccountKey=GftK4dm+kC4o8uPAjLJLJz1oBBX7pw3/xGY8cVumnV3yTwE1p2ISkPESDDUtzL2EvWFfHURFfMMR+AStVVa+MA==;EndpointSuffix=core.windows.net"
## define container name from azure storage account
blob_container_name = "mysql-image"


twilio_account_sid = 'AC1b77fa8c87f235e9a7b28706dd8481a9'
twilio_auth_token = "d27ac42d38ffabb39c7efdea6a68c544"
twilio_phone_number = '+13187193338'

db = SQLAlchemy(app)



def validate_connection_string(connection_string):
    try:
        BlobServiceClient.from_connection_string(connection_string)
        return True
    except Exception as e:
        print(e)
        return False

def upload_blob(image_data, blob_name, connection_string, container_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)

        #  image data sent to azure MUST be base64 encoded, otherwise it will not be able to decode the image
        # Decode the base64 image data
        decoded_image_data = base64.b64decode(image_data)

        # Create a ContentSettings object with the content type set to 'image/png'
        content_settings = ContentSettings(content_type='image/png')

        # Upload the blob with the specified content settings
        blob_client.upload_blob(decoded_image_data, content_settings=content_settings)

        # Return the blob URL
        return blob_client.url
    except Exception as e:
        print(e)
        return None


class Order(db.Model):
    __tablename__ = 'Order'

    orderID = db.Column(db.Integer, primary_key=True)


class User(db.Model):
    __tablename__ = 'User'

    userID = db.Column(db.Integer, primary_key=True)

  

class Refund(db.Model):
    # this is azure sql server table
    __tablename__ = 'Refund'
    refundID = db.Column(db.String(36), primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('User.userID'), nullable=False)  # User ID
    supplierID = db.Column(db.Integer, db.ForeignKey('User.userID'), nullable=False)  # Supplier ID
    orderID = db.Column(db.Integer, db.ForeignKey('Order.orderID'), nullable=False)  # Order ID
    description = db.Column(db.String(255), nullable=False)  # Description
    pic = db.Column(db.String(255), nullable=False)  # Picture
    refundStatus = db.Column(db.String(64), nullable=False)  # Refund status
    refund_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Refund timestamp

    # Initialize Refund object
    def __init__(self, refundID, userID, supplierID, orderID, description, pic, refundStatus):
        self.refundID = refundID  # Set refund ID
        self.userID = userID  # Set user ID
        self.supplierID = supplierID  # Set supplier ID
        self.orderID = orderID  # Set order ID
        self.description = description  # Set description
        self.pic = pic  # Set picture
        self.refundStatus = refundStatus  # Set refund status




#route to the root directory
@app.route('/')

# Method to return all the refunds by using GET method
@app.route("/refund", methods=['GET'])
def get_all_refunds():
    refund_list = db.session.query(Refund).all()  # Query all refunds

    if len(refund_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "refunds": [{"refundID": refund.refundID, "userID": refund.userID, "supplierID": refund.supplierID, 
                                 "orderID": refund.orderID, "description": refund.description, 
                                 "pic": refund.pic, "refundStatus": refund.refundStatus, 
                                 "refund_timestamp": refund.refund_timestamp,
                                 "supplierID": refund.supplierID} 
                                for refund in refund_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no refunds."
        }
    ), 404



# Method to return all refunds for a specific supplier by using supplierID
@app.route("/refund/supplier/<int:supplierID>", methods=['GET'])
def get_refunds_by_supplier(supplierID):
    refund_list = db.session.query(Refund).filter(Refund.supplierID == supplierID).all()  # Query refunds by supplierID

    if len(refund_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "refunds": [{"refundID": refund.refundID, "orderID": refund.orderID, 
                               "description": refund.description, "pic": refund.pic, 
                               "refundStatus": refund.refundStatus, "refund_timestamp": refund.refund_timestamp, 
                               "supplierID": refund.supplierID, "userID": refund.userID} 
                              for refund in refund_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No refunds found for this supplier."
        }
    ), 404



# Method to return the specific refund by using refundID
@app.route("/refund/<string:refundID>", methods=['GET'])
def find_by_refundID(refundID):
    refund = db.session.query(Refund).get(refundID)

    if refund:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "refundID": refund.refundID, 
                    "userID": refund.userID, 
                    "supplierID": refund.supplierID, 
                    "orderID": refund.orderID, 
                    "description": refund.description, 
                    "pic": refund.pic, 
                    "refundStatus": refund.refundStatus, 
                    "refund_timestamp": refund.refund_timestamp
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Refund not found."
        }
    ), 404



# Create Refund by using POST
@app.route("/refund", methods=['POST'])
def create_refund():
    data = request.get_json()
    refundID = str(uuid4())  # Generate a unique refundID

    # Validate Azure connection string
    if not validate_connection_string(connec_string):
        return jsonify(
            {
                "code": 500,
                "message": "Invalid Azure connection string."
            }
        ), 500

    # Get the image data from the request data JSON key
    image_data = data.get('pic')

    # Generate a unique blob name based on the refund ID
    blob_name = "refund_image_" + refundID 

    # Upload image to Azure and get the blob URL
    blob_url = upload_blob(image_data, blob_name, connec_string, blob_container_name)
    if not blob_url:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while uploading the image to Azure."
            }
        ), 500

    refund = Refund(refundID, data['userID'], data['supplierID'], data['orderID'], data['description'], blob_url, data['refundStatus'])

    try:
        db.session.add(refund)
        db.session.commit()


        
    except Exception as e:
        print(e)
        return jsonify(
            {
                "code": 500,
                "data": {
                    "refundID": refundID
                },
                "message": "An error occurred creating the refund."
            }
        ), 500

    if not all(key in data for key in ('userID', 'supplierID', 'orderID', 'description', 'pic', 'refundStatus')):
        return jsonify(
            {
                "code": 400,
                "message": "Missing or invalid data."
            }
        ), 400

    return jsonify(
        {
            "code": 201,
            "data": {
                "refundID": refund.refundID, 
                "userID": refund.userID, 
                "supplierID": refund.supplierID, 
                "orderID": refund.orderID, 
                "description": refund.description, 
                "pic": refund.pic, 
                "refundStatus": refund.refundStatus, 
                "refund_timestamp": refund.refund_timestamp
            }
        }
    ), 201


#Update refund status through refundID 
@app.route('/refund/<refundID>', methods=['PUT'])
def update_refund(refundID):
    refund = Refund.query.filter_by(refundID=refundID).first()
    if refund is None:
        return jsonify(
            {
                "code": 404,
                "message": "Refund not found."
            }
        ), 404

    # Get the new status from the request body
    new_status = request.json.get('refundStatus')

    if new_status not in ['approved', 'rejected']:
        return jsonify(
            {
                "code": 400,
                "message": "Invalid refund status. Must be 'approved' or 'rejected'."
            }
        ), 400

    refund.refundStatus = new_status
    db.session.commit()

    return jsonify(
        {
            "code": 200,
            "data": {
                "refundID": refundID,
                "refundStatus": new_status
            },
            "message": "Refund status has been updated."
        }
    ), 200

if __name__ == '__main__':
  
    app.run(host='0.0.0.0', port=5002, debug=True)



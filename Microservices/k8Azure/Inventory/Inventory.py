from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import ForeignKey

app = Flask(__name__)
CORS(app)

##to run locally (assuming you have phpmyadmin table all set up)
##app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#This is to run from azure database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)


db = SQLAlchemy(app)

class Inventory(db.Model):

     # this is azure sql server table
    __tablename__ = 'Inventory'
    
    fishID = db.Column(db.Integer, primary_key=True)  # Fish ID
    userID = db.Column(db.Integer, ForeignKey('user.userID'), nullable=False)  # User ID
    itemName = db.Column(db.String(100), nullable=False)  # Item Name
    description = db.Column(db.String(255), nullable=False)  # Description
    price = db.Column(db.Float, nullable=False)  # Price
    qty = db.Column(db.Integer, nullable=False)  # Quantity

    # Initialize Inventory object
    def __init__(self, fishID, userID, itemName, description, price, qty):
        self.fishID = fishID  # Set fish ID
        self.userID = userID  # Set user ID
        self.itemName = itemName  # Set item name
        self.description = description  # Set description
        self.price = price  # Set price
        self.qty = qty  # Set quantity



#route to the root directory
@app.route('/')

#method to return the number of inventory_records in azure database
def index():
    inventory_rec = Inventory.query.all()
    return 'Number of inventory_records: %d' % len(inventory_rec)


# Method to return all the inventory items by using GET method
@app.route("/inventory", methods=['GET'])
def get_all_inventory_items():
    inventory_list = db.session.query(Inventory).all()  # Query all inventory items

    if len(inventory_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "inventory": [{"fishID": inventory.fishID, "userID": inventory.userID,
                                   "itemName": inventory.itemName, "description": inventory.description,
                                   "price": inventory.price, "qty": inventory.qty} 
                                  for inventory in inventory_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no inventory items."
        }
    ), 404

@app.route("/inventory/seller/<int:userID>", methods=['GET'])
def get_seller_inventory_items(userID):
    inventory_list = db.session.query(Inventory).filter(Inventory.userID == userID).all()  # Query all inventory items

    if len(inventory_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "inventory": [{"fishID": inventory.fishID, "userID": inventory.userID,
                                   "itemName": inventory.itemName, "description": inventory.description,
                                   "price": inventory.price, "qty": inventory.qty} 
                                  for inventory in inventory_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no inventory items."
        }
    ), 404

# Method to return the specific inventory item by using fishID
@app.route("/inventory/<int:fishID>", methods=['GET'])
def find_by_fishID(fishID):
    inventory = db.session.query(Inventory).get(fishID)

    if inventory:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "fishID": inventory.fishID, 
                    "userID": inventory.userID,
                    "itemName": inventory.itemName, 
                    "description": inventory.description,
                    "price": inventory.price, 
                    "qty": inventory.qty
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Inventory item not found."
        }
    ), 404

# Create Inventory by using POST
@app.route("/inventory", methods=['POST'])
def create_inventory_item():
    data = request.get_json()
    fishID = data['fishID']
    if db.session.query(Inventory).get(fishID):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "fishID": fishID
                },
                "message": "Inventory item already exists."
            }
        ), 400

    inventory = Inventory(fishID, data['userID'], data['itemName'], data['description'], data['price'], data['qty'])

    try:
        db.session.add(inventory)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "fishID": fishID
                },
                "message": "An error occurred creating the inventory item."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": {
                "fishID": inventory.fishID, 
                "userID": inventory.userID,
                "itemName": inventory.itemName, 
                "description": inventory.description,
                "price": inventory.price, 
                "qty": inventory.qty
            }
        }
    ), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)



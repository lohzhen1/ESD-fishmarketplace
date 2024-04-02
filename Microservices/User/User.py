from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import ForeignKey

app = Flask(__name__)
CORS(app)

##To run locally (assuming you have phpmyadmin table all set up)
##app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/user'


#This is to run from azure database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://admin1:S1234567z!@esdmysql.database.windows.net:1433/ESD?"
    "driver=ODBC+Driver+18+for+SQL+Server"
)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False





db = SQLAlchemy(app)

class User(db.Model):

     # this is azure sql server table
    __tablename__ = 'User'

    userID = db.Column(db.Integer, primary_key=True)  # User ID
    username = db.Column(db.String(64), nullable=False)  # Username
    displayName = db.Column(db.String(100), nullable=False)  # Username
    password = db.Column(db.String(255), nullable=False)  # Password
    userType = db.Column(db.String(64), nullable=False)  # User type
    deliveryAddress = db.Column(db.String(64), nullable=False)  # Delivery address
    contactNum = db.Column(db.String(64), nullable=False)  # Contact number
    cartID = db.Column(db.String(64), nullable=True)  # Contact number
    email = db.Column(db.String(64), nullable=False)  # Contact number

    # Initialize User object
    def __init__(self, userID, username, displayName, userType, deliveryAddress, contactNum, password, cartID, email):
        self.userID = userID  # Set user ID
        self.username = username  # Set username
        self.displayName = displayName  # Set username
        self.password = password  # Set username
        self.userType = userType  # Set user type
        self.deliveryAddress = deliveryAddress  # Set delivery address
        self.contactNum = contactNum  # Set contact number
        self.cartID = cartID  # Set delivery address
        self.email = email  # Set contact number


#route to the root directory
@app.route('/')


#method to return the number of user_records in azure database
def index():
    user_rec = User.query.all()
    return 'Number of user: %d' % len(user_rec)

# Method to return all the users by using GET method
@app.route("/user", methods=['GET'])
def get_all_users():
    user_list = db.session.query(User).all()  # Query all users

    if len(user_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "users": [{"userID": user.userID, "username": user.username, "userType": user.userType, "password": user.password,
                               "deliveryAddress": user.deliveryAddress, "contactNum": user.contactNum, "displayName": user.displayName,
                                "cartID": user.cartID, "email": user.email} 
                              for user in user_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404

# Method to return the specific user by using userID
@app.route("/user/<int:userID>", methods=['GET'])
def find_by_userID(userID):
    user = db.session.query(User).get(userID)

    if user:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "userID": user.userID, 
                    "username": user.username,
                    "displayName": user.displayName, 
                    "userType": user.userType, 
                    "deliveryAddress": user.deliveryAddress, 
                    "contactNum": user.contactNum,
                    "password": user.password,
                    "cartID": user.cartID, 
                    "email": user.email
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

# Method to login 
@app.route("/user/login", methods=['POST'])
def find_by_username():

    data = request.get_json()
    loginUsername = data['username']
    loginPassword = data['password']

    user = db.session.scalars(db.select(User).filter_by(username = loginUsername, password = loginPassword).limit(1)).first()

    if user:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "userID": user.userID, 
                    "username": user.username,
                    "displayName": user.displayName, 
                    "userType": user.userType, 
                    "deliveryAddress": user.deliveryAddress, 
                    "contactNum": user.contactNum,
                    "password": user.password,
                    "cartID": user.cartID, 
                    "email": user.email
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

# Create User by using POST
@app.route("/user", methods=['POST'])
def create_user():
    data = request.get_json()
    userID = data['userID']
    if db.session.query(User).get(userID):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "userID": userID
                },
                "message": "User already exists."
            }
        ), 400

    user = User(userID, data['username'], data["displayName"], data['userType'], data['deliveryAddress'], data['contactNum'], data['password'], data['cartID'] , data['email']) 

    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "userID": userID
                },
                "message": "An error occurred creating the user."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": {
                "userID": user.userID, 
                "username": user.username,
                "displayName": user.displayName, 
                "userType": user.userType, 
                "deliveryAddress": user.deliveryAddress, 
                "contactNum": user.contactNum,
                "password": user.password,
                "cartID": user.cartID, 
                "email": user.email
            }
        }
    ), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)



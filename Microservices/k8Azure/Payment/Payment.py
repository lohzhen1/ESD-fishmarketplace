import os
import uuid

import stripe
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import logging


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# configure stripe
stripe_keys = {
    'secret_key': "sk_test_51OtOURF9l86t97fe4G8GWJWeh1oqqh8ErO0yd8s9BQEs3wo7iNgPFGbcuZoPKZtbo2cyFqZZRnqfWBSdTldndVaJ00a3Qlgkig",
    'publishable_key': "pk_test_51OtOURF9l86t97feBe0E87BySfcoGrWPZiC9vNV0qdGsl2iSclbsy4CN4qO2fiTRonIo2M0WezNv8oU1sC3ALapE0051Z00Pi3",
}

stripe.api_key = stripe_keys['secret_key']

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/config')
def get_publishable_key():
    stripe_config = {'publicKey': stripe_keys['publishable_key']}
    return jsonify(stripe_config)

#Line items describes all the items in the transaction
# example of what to pass in the body
# [
#     {
#         "itemName": "itemName",
#         "subTotal": "subTotal",
#         "qty": "qty"
#     },
#     {
#         "itemName": "itemName",
#         "subTotal": "subTotal",
#         "qty": "qty"
#     }
# ]
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Creates a new checkout session for the payment.

    Returns:
        A JSON response containing the session ID of the created checkout session.
    """
    domain_url = 'http://localhost:5173'

    try:
        data = json.loads(request.data)
        # Display the JSON data in the terminal
        logging.info("Received data: %s", data)
        items = []
        if 'subTotal' in data[0]:
            for d in data:
                temp = {
                    'price_data': {
                        'currency': 'sgd',
                        'unit_amount': int(d["subTotal"]) * 100,
                        'product_data': {
                            'name': d["itemName"],
                            # 'description': 'Comfortable cotton t-shirt',
                            # 'images': ['https://example.com/t-shirt.png'],
                        },
                    },
                    'quantity': d["qty"],
                }
                items.append(temp)
        else:
            for d in data:
                temp = {
                    'price_data': {
                        'currency': 'sgd',
                        'unit_amount': int(d["price"]) * 100,
                        'product_data': {
                            'name': d["itemName"],
                            # 'description': 'Comfortable cotton t-shirt',
                            # 'images': ['https://example.com/t-shirt.png'],
                        },
                    },
                    'quantity': d["qty"],
                }
                items.append(temp)
        print(items)

        # create new checkout session
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url +
            '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + '/cancelled',
            payment_method_types=['card'],
            mode='payment',
            line_items=items
            # [
            #     {
                    # 'name': book_to_purchase['title'],
                    # 'currency': 'SGD',
                    # 'amount': round(float(book_to_purchase['price']) * 100),
                    # 'price_data': {
                    # 'currency': 'sgd',
                    # 'unit_amount': 2000,
                    # 'product_data': {
                    #     'name': 'T-shirt',
                    #     'description': 'Comfortable cotton t-shirt',
                        # 'images': ['https://example.com/t-shirt.png'],
            #         },
            #         },
            #         'quantity': 1,
            #     },
            # ]
        )
        return jsonify({'code': 200, 'sessionId': checkout_session['id']}), 200
    except Exception as e:
        return jsonify({'code': 403, 'message': str(e)}), 403

# Pass in { checkoutID : "123" } in body
@app.route('/payment/refund', methods=['POST'])
def refund():
    try:
        data = request.get_json()

        checkout = stripe.checkout.Session.retrieve(data["checkoutID"])
        
        refund = stripe.Refund.create(payment_intent=checkout.payment_intent)

        return jsonify({'code': 200, 'status': refund.status}), 200 
    except Exception as e:
        return jsonify({'code': 404, 'message': str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)



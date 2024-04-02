<script setup>
import axios from 'axios';

</script>
<template>

    <body>
        <div class="container">
            <h1>Cart</h1>
            <div class="row">
                <div class="col-8 border content">
                    <h5>Items</h5>
                    <ul class="list-group list-group-flush ">
                        <li class="list-group-item list-group-item-action" v-for="(item, index) in cart" :key="index">
                            <div class="row">
                                <div class="col-xl-2 col-md-4">
                                    <!-- Change image later -->
                                    <img src="../assets/fish.png" class="img-list" alt="...">
                                </div>
                                <div class="col-xl-10 col-md-8">
                                    <div class="d-flex w-100 justify-content-between">
                                        <h5 class="mb-1">
                                            {{ item.itemName }}
                                        </h5>
                                        <h5>Total price: {{ '$' + (item.price * item.qty).toFixed(2) }}</h5>
                                    </div>
                                    <p class="mb-1">Quantity: {{ item.qty }}</p>
                                    <!-- Remove KG since there's no weight -->
                                    <!-- <p class="mb-1">{{ item.weight + 'kg' }}</p> -->
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="col-4 border content">
                    <h5>Payment Methods</h5>
                    <ul class="list-group list-group-flush ">
                        <li class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">Total</h5>
                                <!-- Computes total price -->
                                <h5>{{ '$' + totalPrice.toFixed(2) }}</h5>
                            </div>
                        </li>
                    </ul>
                    <div class="row">
                        <div class="col">
                            <!-- Commented out for Jiawei Testing -->
                            <!-- <button type="submit" class="w-100 btn btn-dark btn-lg"
                                style="padding-left: 2.5rem; padding-right: 2.5rem;"
                                @click="handlePurchaseBook()">Pay</button> -->
                            <button type="submit" class="w-100 btn btn-dark btn-lg"
                                style="padding-left: 2.5rem; padding-right: 2.5rem;"
                                @click="handlePayment()">Pay</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
</template>
<style scoped>
.content {
    min-height: 500px;
    padding: 20px;
    overflow-y: scroll;
}

.img-list {
    height: 100px;
    width: 100px;
}
</style>
<script>
export default {

    mounted() {
    },

    computed: {
        /**
         * Calculates the total price of the items in the cart.
         * @returns {number} The total price of the items in the cart.
         */
        totalPrice() {
            return Array.isArray(this.cart)
                ? this.cart.reduce((total, item) => total + item.price * item.qty, 0)
                : 0;
        }
    },

    data() {
        return {
            userID: this.userID, //Retrieve userID later user.data.userID
            cart: [],
            stripe: null,
            // Why are we passing in Book ?
            book: {
                id: 1,
            }
        }
    },

    /** Methods to run
     *  user.py
     *  cart.py
     *  cart_item.py
     *  payment.py
     *  order.py
     *  order_details.py
     *  reservation.py
     *  
     */


    created() {
        this.user = JSON.parse(sessionStorage.getItem("user"));
        console.log(this.user);
        if (this.user) {
            this.userID = this.user.data.userID;
            this.loggedIn = this.user.loggedIn;
            this.cartID = this.user.data.cartID;
            this.deliveryAddress = this.user.data.deliveryAddress;
        }
        this.getCartByUserId(this.userID);
        this.getStripePublishableKey();
        
    },
    methods: {
        getStripePublishableKey() {
            // fetch('http://localhost:5011/config')
            fetch('http://57.151.9.8/config')
                .then((result) => result.json())
                .then((data) => {
                    // Initialize Stripe.js
                    this.stripe = Stripe(data.publicKey);
                });
        },

        /**
         * Handles the payment process by creating a checkout session and redirecting to Stripe Checkout.
         * 
         * @method handlePayment
         * @returns {void}
         */
        handlePayment() {
            // Get Checkout Session ID
            console.log(JSON.stringify(this.cart))
            // fetch('http://localhost:5011/create-checkout-session', {
            fetch('http://57.151.9.8/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.cart),
            })
                .then((result) => result.json())
                .then((data) => {
                    console.log(data);
                    // Redirect to Stripe Checkout
                    sessionStorage.setItem("cartCheckout", JSON.stringify(        
                    {
                        "userID": this.userID,
                        "cartID": this.cartID,
                        "deliveryAddress": this.deliveryAddress,
                        "total_price": this.totalPrice,
                        // Pass fishID, itemName, qty pass this as an array
                        "cartItems": this.cart,
                        "checkoutID": data.sessionId
                        })
                    )     

                    return this.stripe.redirectToCheckout({ sessionId: data.sessionId });
                })
                .then((res) => {
                    console.log(res);
                });
        },

        /**
         * Retrieves the cart for a specific user by making a GET request to the backend API.
         *
         * @param {type} userId - the ID of the user for whom the cart is being retrieved
         * @return {type} undefined - this function does not return a value directly
         */
        getCartByUserId(userId) {
            // axios.get(`http://localhost:5105/retrieve_cart_items/${userId}`)
            axios.get(`http://57.151.9.8/retrieve_cart_items/${userId}`)
                .then(response => {
                    this.cart = response.data;
                    console.log("Cart")
                    console.log(this.cart);
                })
                .catch(error => {
                    console.error(error);
                });
        },

        // Not used anymore 
        handleReservationPayment() {
            // Handle reservation payment
            console.log("Items inside cart for payment: ");
            console.log(this.cart);
            // axios.post('http://localhost:5090/handle_reservation_payment', {
            axios.post('http://57.151.9.8/handle_reservation_payment', {
                userID: this.userID,
                cartID: this.cartID,
                deliveryAddress: this.deliveryAddress,
                total_price: this.totalPrice,
                // Pass fishID, itemName, qty pass this as an array
                cartItems: this.cart
            })
                // With response reload the page
                .then(response => {
                    console.log(response);
                })
                .catch(error => {
                    console.error(error);
                });
        }
    },
}
</script>
<script setup>
import axios from 'axios';



</script>
<template>


    <body>
        <!-- Only if user is logged in will they be able to see their reservations -->
        <div v-if="this.loggedIn" class="container">
            <!-- fetchReservations() -->
            <h1>Reserved Fishes</h1>
            <div class="row row-cols-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-6 g-4">
                <!-- No date is checked here, just displaying everything being returned from reservationList -->
                <div v-for="reservation in reservationList" :key="reservation.reserveID" class="col">
                    <!-- Check if fish exists -->
                    <div v-if="fishes.some(fish => fish.fishID === reservation.fishID)" class="col">
                        <div class="card h-100">
                            <!-- Using default image for now, need to add image field in inventory? -->
                            <img src="../assets/fish.png" class="card-img-top" alt="Fish Image">
                            <div class="card-body">
                                <h5 class="card-title">Price: ${{ fishes.find(fish => fish.fishID ===
            reservation.fishID).price }}</h5>
                                <p class="card-text">
                                    {{ fishes.find(fish => fish.fishID === reservation.fishID).itemName }}
                                    <br>
                                    Quantity: {{ fishes.find(fish => fish.fishID === reservation.fishID).qty }}
                                    <br>
                                    <small class="text-muted">Reserved on {{ reservation.reserve_timestamp }}</small>
                                </p>
                                <div class="text-center">
                                    <button type="button" class="btn btn-outline-info"
                                        @click="addToCartReservation(reservation)">Add to Cart</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="container">
            <!-- fetchInventory() -->
            <h1>Marketplace</h1>
            <div class="row row-cols-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-6 g-4">
                <div v-for="fish in fishes" :key="fish.fishID" class="col">
                    <div class="card h-100">
                        <!-- Using default image for now, need to add image field in inventory? -->
                        <img src="../assets/fish.png" class="card-img-top" alt="Fish Imag">
                        <div class="card-body">
                            <h5 class="card-title">Price: ${{ fish.price }}</h5>
                            <p class="card-text">
                                {{ fish.itemName }}
                                <br>
                                Quantity: {{ fish.qty }}
                                <br>
                                <small class="text-muted">5kg</small>
                            </p>
                            <div class="text-center">
                                <!-- Display "Sold Out" button if fish is out of stock and user ordered it -->
                                <!-- Review this logic -->
                                <button v-if="fish.qty == 0 && orders.includes(fish.fishID)" type="button"
                                    class="btn btn-outline-info btn-disabled" disabled> <i class="fa fa-bookmark"></i>
                                    Sold Out </button>
                                <!-- Display "Reserve Fish" button if fish is out of stock and user has not reserved it -->
                                <!-- Review this logic -->
                                <button v-if="fish.qty == 0 && !orders.includes(fish.fishID)" type="button"
                                    class="btn btn-outline-info" @click="reserveFish(fish.fishID)"
                                    :disabled="!loggedIn || reservationList.some(item => item.fishID === fish.fishID)"
                                    :class="{ 'btn-disabled': !loggedIn || reservationList.some(item => item.fishID === fish.fishID) }">
                                    <i class="fa fa-bookmark"></i> Reserve Fish
                                </button>
                                <!-- Display "Add to Cart" button if fish is in stock -->
                                <button v-if="fish.qty > 0" @click="addToCart(fish)" class="btn btn-outline-info">
                                    <i class="fa fa-bookmark"></i> Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>


</template>
<style scoped>
.container {
    margin-bottom: 20px;
}

.btn-disabled {
    background-color: grey;
    color: white;
    cursor: not-allowed;
}
</style>
<script>
export default {

    mounted() {

    },
    data() {
        return {
            fishes: [],
            orders: [],
            reservationList: [],
            user: null,
        };
    },
    /** Methods to Run
     *  user.py Check for user Login
     *  inventory.py To Retrieve Inventory Items
     *  retrieve_order_details.py Retrieve Order made by User Today & get the FishID for those orders
     *  orders.py 
     *  order_details.py
     *  reservation.py To Retrieve Reservation made by user
     *  add_reserved_fish.py Add Reservered Fish to Cart
     *  cart.py
     */

    /**
     *
     * This hook is used to fetch the initial data for the component.
     * It makes two API calls, one to fetch the orders and another to fetch the inventory.
     */
    created() {
        // Fetch the user
        this.user = JSON.parse(sessionStorage.getItem("user"));
        if (this.user) {
            this.userID = this.user.data.userID;
            this.loggedIn = this.user.loggedIn;
            this.cartID = this.user.data.cartID;
        }
        console.log(this.user);
        console.log(this.loggedIn);
        console.log(this.userID);
        console.log(this.cartID);
        // Fetch the inventory
        this.fetchInvetory();
        // Fetch the orders
        this.fetchOrders();
        // Fetch the reservation list
        this.fetchReservations();
        // console.log("User: ", this.user);
        // console.log("loggedin: ", this.user.loggedIn);
    },

    methods: {
        /**
         * Fetches the orders for the current user from the server.
         *
         * @param {type} paramName - description of parameter
         * @return {type} description of return value
         */
        fetchOrders() {
            // axios.get(`http://localhost:5110/retrieve_order_details/${this.userID}`)
            axios.get(`http://57.151.9.8/retrieve_order_details/${this.userID}`)
                .then(response => {
                    this.orders = response.data;
                    console.log("Orders for current user: ");
                    console.log(this.orders);
                })
                .catch(console.log);
        },

        /**
         * Reserve a fish with the given fishID.
         *
         * @param {type} fishID - The ID of the fish to be reserved
         * @return {type} description of return value
         */
        reserveFish(fishID) {
            // Check if fishID and userID are integers
            if (typeof fishID === 'number' && Number.isInteger(fishID)) {
                // axios.post('http://localhost:5003/reservation/create', { fishID: fishID, userID: this.userID })
                axios.post('http://57.151.9.8/reservation/create', { fishID: fishID, userID: this.userID })
                    .then(response => {
                        console.log(response);
                        // Handle the response
                        //Do a alert  to show reservation added
                        alert("Reservation Added");
                        this.fetchReservations();
                    })
                    .catch(error => {
                        if (error.response) {
                            // The request was made and the server responded with a status code
                            // that falls out of the range of 2xx
                            console.log("Error response data: ", error.response.data);
                            console.log("Error response status: ", error.response.status);
                            console.log("Error response headers: ", error.response.headers);
                        } else if (error.request) {
                            // The request was made but no response was received
                            console.log("Error request: ", error.request);
                        } else {
                            // Something happened in setting up the request that triggered an Error
                            console.log('Error', error.message);
                        }
                        console.log("Error config: ", error.config);
                    });
            } else {
                console.log("Invalid fishID or userID");
            }
        },

        /**
         * Fetch the reservation list for the user
         */
        fetchReservations() {
            // axios.get(`http://localhost:5003/reservation/${this.userID}`)
            axios.get(`http://57.151.9.8/reservation/${this.userID}`)
                .then(response => {
                    // Assign the fetched reservation list to the component's reservationList data property
                    this.reservationList = response.data.data.reservations;

                    // Log the fetched reservation list to the console
                    console.log("Reservation List: ");
                    console.log(this.reservationList);
                })
                .catch(error => {
                    // Log any errors that occur during the API call
                    this.reservationList = [];
                });
        },

        /**
         * Fetch the inventory from the specified URL using axios and assign the fetched inventory to the component's fishes data property. 
         * Log the fetched inventory to the console and log any errors that occur during the API call.
         *
         * @param None
         * @return None
         */
        fetchInvetory() {
            // Fetch the inventory
            // axios.get('http://localhost:5006/inventory')
            axios.get('http://57.151.9.8/inventory')
                .then(response => {
                    // Assign the fetched inventory to the component's fishes data property
                    this.fishes = response.data.data.inventory;

                    // Log the fetched inventory to the console
                    console.log("Inventory of Fishes: ");
                    console.log(this.fishes);
                })
                .catch(error => {
                    // Log any errors that occur during the API call
                    console.log(error);
                });
        },

        /**
         * Adds a reservation to the cart.
         *
         * @param {Object} reservation - the reservation to be added to the cart
         * @return {void} 
         */
        addToCartReservation(reservation) {
            // Performing Searching to get the FishName & Price
            let fishID = reservation.fishID
            let fish = this.fishes.find(fish => fish.fishID === fishID);
            if (fish) {
                reservation.itemName = fish.itemName;
                reservation.price = fish.price;
                // Problem will occur when qty > 1
                reservation.qty = 1;
                reservation.cartID = this.cartID;
            }
            // Logging
            console.log(reservation);
            // Firstly add to cart_item,
            // axios.post(`http://localhost:5125/add_reserved_fish`, reservation)
            axios.post(`http://57.151.9.8/add_reserved_fish`, reservation)
                .then(response => {
                    console.log(response);
                    if (response.status === 201) {
                        // If add to cart return status 201, remove reservation by using reservationID
                        this.fetchReservations();

                        alert("Successfully added reserved fish to cart & removed from reservation");
                    }
                    else {
                        console.log("Failed to add reservation to cart");
                    }
                })
                .catch(error => {
                    console.log(error);
                });
        },

        /**
         * Add a fish to the cart.
         *
         * @param {Object} fish - The fish to be added to the cart
         * @return {void} 
         */
        addToCart(fish) {
            console.log("Adding to cart: ", fish);
            // Check if fishID is integer
            if (typeof fish.fishID === 'number' && Number.isInteger(fish.fishID)) {
                // Add the fish to the cart
                // axios.post(`http://localhost:5062/cart_items/${this.cartID}/add_fish`, { fishID: fish.fishID, itemName: fish.itemName, qty: 1, price: fish.price })
                axios.post(`http://57.151.9.8/cart_items/${this.cartID}/add_fish`, { fishID: fish.fishID, itemName: fish.itemName, qty: 1, price: fish.price })
                    .then(response => {
                        console.log(response);
                        if (response.statusText === 'Created') {
                            console.log("Successfully added to cart");
                            alert("Fish Added to Cart");
                        }
                    })
                    .catch(error => {
                        if (error.response) {
                            // The request was made and the server responded with a status code
                            // that falls out of the range of 2xx
                            console.log("Error response data: ", error.response.data);
                            console.log("Error response status: ", error.response.status);
                            console.log("Error response headers: ", error.response.headers);
                        } else if (error.request) {
                            // The request was made but no response was received
                            console.log("Error request: ", error.request);
                        } else {
                            // Something happened in setting up the request that triggered an Error
                            console.log('Error', error.message);
                        }
                        console.log("Error config: ", error.config);
                    });
            } else {
                console.log("Invalid fishID or userID");
            }
        },
    },


}

</script>
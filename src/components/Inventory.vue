<script setup>

</script>
<template>
    <body>
        <div class="container">
            <h1>Inventory</h1>
            <div class="row row-cols-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-6 g-4">
                <div v-for="fish in fishes" :key="fish.fishID" class="col">
                    <div class="card h-100">
                        <!-- Using default image for now, need to add image field in inventory? -->
                        <img src="../assets/fish.png" class="card-img-top" alt="Fish Image">
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
                                <button type="button" class="btn btn-outline-info" v-if="fish.qty > 0" @click="createAuction(fish)">
                                    <i class="fa fa-gavel"></i>
                                    <span> Add to Auction</span>
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

</style>
<script>
import router from '../router/index.js'

export default {

    mounted() {
        console.log(this.user);
        // this.getInventory();
    },
    data(){
        return{
            user: JSON.parse(sessionStorage.getItem("user")),
            fishes: [
                        {
                            "description": "Description for Fish Item 1",
                            "fishID": 1,
                            "itemName": "Fish Item 1",
                            "price": 10,
                            "qty": 2,
                            "userID": 3
                        },
                        {
                            "description": "Description for Fish Item 2",
                            "fishID": 2,
                            "itemName": "Fish Item 2",
                            "price": 20,
                            "qty": 3,
                            "userID": 3
                        },
                        {
                            "description": "A high-quality fish renowned for its taste.",
                            "fishID": 3,
                            "itemName": "BlueFin Tuna",
                            "price": 200,
                            "qty": 0,
                            "userID": 3
                        }
                    ]
        }
    },
    methods: {
        getInventory() {
            fetch('http://57.151.9.8/inventory/seller/' + this.user.data.userID)
                .then((result) => result.json())
                .then((data) => {
                this.fishes = data.data.inventory
                console.log(this.fishes)
            });
        },
        createAuction(fish) {
            var now = new Date()

            var auction = {
                'fishID': fish.fishID, 
                'winnerID': null,
                'winnerName': "", 
                'currentPrice': fish.price, 
                'timestart': now, 
                'status': "Inactive", 
                'timeEnd': now, 
                'itemName': fish.itemName
            }
            console.log(auction)
            fetch('http://localhost:5007/auction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(auction)
                })
                .then((result) => result.json())
                .then((data) => {
                    // console.log(data)
            });
        },
    },
    

}
</script>
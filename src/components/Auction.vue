<script setup>

</script>
<template>
    <body>
        <div class="container">
            <h1>Auction</h1>
            <div class="row">
                <h5>Demo Purpose</h5>
                <div class="col">
                    <button class="btn btn-outline-success w-100" @click="resetAuction()">Reset Auctions</button>
                </div>
                <div class="col">
                    <button class="btn btn-outline-danger w-100" @click="endAuction()" >End all Auctions</button>
                </div>
                <div class="col">
                    <button class="btn btn-outline-warning w-100" @click="checkSettlement()">Check Settlement</button>
                </div>
            </div>
            <br>
            <div class="row row-cols-2 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 g-4" v-if="auctions != []">
                <div class="col" v-for="auction in auctions">
                    <div class="card h-100">
                        <img src="../assets/fish.png" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">{{ auction.itemName }}</h5>
                            <p class="card-text">
                                Current Bid: ${{ auction.currentPrice }}
                                <br>
                                    Current Bidder:
                                <span v-if="auction.winnerName">
                                    {{ auction.winnerName }}
                                </span>
                                <span v-else>
                                    No Winner
                                </span>
                                <br>
                                Time left for bidding: 
                                <br>
                                <b :id="auction.auctionID + 'time'"></b>
                                <br>
                                <!-- <small class="text-muted">5kg</small> -->
                            </p>
                            <div class="text-center" v-if="auction.status == 'Active' && new Date(auction.timeEnd).getTime() > new Date().getTime()">
                                <div class="form-floating mb-3">
                                    <input type="number" :min="parseInt(auction.currentPrice) + 1" step="1" class="form-control" :id="auction.auctionID +'amountInput'"  :value="parseInt(auction.currentPrice) + 1">
                                    <label :for="auction.auctionID +'amountInput'">Bidding Price</label>
                                </div>              
                                <button type="button" class="btn btn-outline-primary" @click="bid(auction)"><i class="fa fa-gavel"></i> Bid</button>
                            </div>
                        </div>
                    </div>
                </div>


            </div>
            <div v-else>
                <h2>No auction today</h2>
            </div>
            <!-- <div class="col">
                    <div class="card h-100">
                        <img src="../assets/fish.png" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">Fresh Fish in box</h5>
                            <p class="card-text">
                                Current Bid: $20
                                <br>
                                Current Bidder: John
                                <br>
                                Time left for bidding: 
                                <br>
                                <b>12:30 Mins</b>
                                <br>
                                <small class="text-muted">5kg</small>
                            </p>
                            <div class="text-center">
                                <div class="form-floating mb-3">
                                    <input type="number" min="20" step="1" class="form-control" id="amountInput" value="20">
                                    <label for="amountInput">Bidding Price</label>
                                </div>              
                                <button type="button" class="btn btn-outline-primary"><i class="fa fa-gavel"></i> Bid</button>
                            </div>
                        </div>
                    </div>
                </div> -->
        </div>

    </body>


</template>
<style scoped>

.container{
    margin-bottom: 20px;
}

</style>
<script>
import io from 'socket.io-client'
import router from '@/router';


export default {

    created() {
        // Get today auction
        this.getTodayAuction()

        // Connect to the Flask-SocketIO server
        this.socket = io('localhost:5007');
        this.socket2 = io('localhost:5100');

        this.setupSocketListeners();
        this.setupSocketListeners2();

        for(let auction of this.auctions){
            this.timeleft(auction.timeEnd, auction.auctionID)
        }
    },
    data(){
        return{
            auctions: [],
            interval: [],
            user: JSON.parse(sessionStorage.getItem("user"))
        }
    },
    methods: {
        getTodayAuction() {
            fetch('http://localhost:5007/auction/today')
                .then((result) => result.json())
                .then((data) => {
                    this.auctions = data.data.auction
                    for(let auction of this.auctions){
                        this.timeleft(auction.timeEnd, auction.auctionID)
                    }
            });
        },
        timeleft(timeEnd, id){
            // Convert to a specific format
            var options = {
                weekday: "short",
                day: "2-digit",
                month: "short",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                timeZone: "Asia/Singapore"                
            };

            var options2 = {
                weekday: "short",
                day: "2-digit",
                month: "short",
                year: "numeric",
                hour: "numeric",
                minute: "2-digit",
                second: "2-digit",
            };
            var auctionEnd = new Date(timeEnd).toLocaleString("en-SG", options2)
            auctionEnd = new Date(auctionEnd).getTime()

            this.interval[id] = setInterval(() => {


                var now = new Date().toLocaleString("en-SG", options);
                
                now = new Date(now).getTime()

                var distance = auctionEnd - now;

                if(distance < 0){
                    document.getElementById(id + 'time').innerHTML =  "AUCTION ENDED"
                }
                else{
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    document.getElementById(id + 'time').innerHTML = hours + 'h ' + minutes + 'm ' + seconds + 's'
                }

            }, 1000)

        },
        bid(auction){
            var bidSubmit = JSON.parse(JSON.stringify(auction))
            bidSubmit.winnerName = this.user.data.displayName
            bidSubmit.winnerID = this.user.data.userID
            bidSubmit.currentPrice = document.getElementById(bidSubmit.auctionID + 'amountInput').value

            console.log(bidSubmit)
            fetch('http://localhost:5100/place_bid', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(bidSubmit)
                })
                .then((result) => result.json())
                .then((data) => {
                    if(data.code == "201"){
                        alert("Bid Successful")
                    }
                    else{
                        alert("Bid Failed")
                    }
                    console.log(data)
            });
            // fetch('http://localhost:5007/auction/'+bidSubmit.auctionID, {
            //         method: 'PUT',
            //         headers: {
            //             'Content-Type': 'application/json'
            //         },
            //         body: JSON.stringify(bidSubmit)
            //     })
            //     .then((result) => result.json())
            //     .then((data) => {
            //         // console.log(data)
            // });
        },
        endAuction(){
            fetch('http://localhost:5102/endAuction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.auctions)
                })
                .then((result) => result.json())
                .then((data) => {
                    alert("All auction has ended")
                    // router.go(0)
                    console.log(data)
            });
        },
        resetAuction(){
            fetch('http://localhost:5007/auction/reset', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify([{
                        "auctionID": 1
                    },
                    {
                        "auctionID": 2
                    }])
                })
                .then((result) => result.json())
                .then((data) => {
                    // this.auctions = data.data.auction
                    console.log(data)
                    fetch('http://localhost:5008/bidding_records/delete', {
                        method: 'DELETE'
                        })
                        .then((result) => result.json())
                        .then((data) => {
                            console.log(data)
                    });
                    // for(let i of this.auctions){
                    //     clearInterval(this.interval[i.auctionID])
                    // }
                    // for(let auction of this.auctions){
                    //     this.timeleft(auction.timeEnd, auction.auctionID)
                    // }
                    alert("Auctions resetted")
            });
        },
        checkSettlement(){
            fetch('http://localhost:5106/checkSettlement', {
                    method: 'GET'
                })
                .then((result) => result.json())
                .then((data) => {
                    alert("Settlement checked")
                    // router.go(0)
            });
        },
        setupSocketListeners(){
            // Listen for 'update' events from the server
            this.socket.on('update', (data) => {
                this.messages = data;
                console.log(data)
                
                if(typeof data !== 'object'){
                    this.auctions = JSON.parse(data)
                }
                else{
                    for(let i = 0; i < this.auctions.length; i++){
                        if(this.auctions[i].auctionID == data.auctionID){
                            this.auctions[i] = data
                            // console.log(this.auctions[i])
                            break;
                        }
                        // console.log(this.auctions[i])
                    }
                }

                for(let i of this.auctions){
                    clearInterval(this.interval[i.auctionID])
                }
                for(let auction of this.auctions){
                    this.timeleft(auction.timeEnd, auction.auctionID)
                }
            });
        },
        setupSocketListeners2(){
            // Listen for 'update' events from the server
            this.socket2.on('update', (data) => {
                this.messages = data;
                console.log(data)
                
                if(typeof data !== 'object'){
                    this.auctions = JSON.parse(data)
                }
                else{
                    for(let i = 0; i < this.auctions.length; i++){
                        if(this.auctions[i].auctionID == data.auctionID){
                            this.auctions[i] = data
                            // console.log(this.auctions[i])
                            break;
                        }
                        // console.log(this.auctions[i])
                    }
                }

                for(let i of this.auctions){
                    clearInterval(this.interval[i.auctionID])
                }
                for(let auction of this.auctions){
                    console.log(auction)

                    this.timeleft(auction.timeEnd, auction.auctionID)
                }
            });
        }
    },
    beforeUnmount() {

        // Disconnect the socket when the component is destroyed
        this.socket.disconnect();

        for(let i of this.auctions){
            clearInterval(this.interval[i.auctionID])
        }

    },


}

</script>
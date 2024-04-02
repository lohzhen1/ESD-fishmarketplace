<script setup>

</script>
<template>
    <body>
        <div class="container-fluid h-custom">
            <div class="row d-flex justify-content-center align-items-center h-100">
                <div class="col-md-8 col-lg-6 col-xl-4 login">
                    <h2 style="margin-top: 20px; margin-bottom: 20px;text-align: center;">
                        Successfully made payment <br><br>
                        <button type="submit" class="w-100 btn btn-outline-success btn-lg"
                            style="padding-left: 2.5rem; padding-right: 2.5rem;" @click="redirect()">
                            Go to Orders
                        </button>
                    </h2>
                </div>
            </div>
        </div>
    </body>
</template>
<style scoped>

</style>
<script>
import router from '@/router';

export default {
    methods: {
        redirect(){
            router.push({ path: 'displayallorders' })
        }
    },
    mounted(){
        var auctionCheckout = JSON.parse(sessionStorage.getItem("auctionCheckout"))
        var cartCheckout = JSON.parse(sessionStorage.getItem("cartCheckout"))

        if(auctionCheckout) {
            var user = JSON.parse(sessionStorage.getItem("user"))
            auctionCheckout["deliveryAddress"] = user["data"]["deliveryAddress"]
            // fetch('http://localhost:5009/order/info/'+ auctionCheckout['orderID'], {
            fetch('http://57.151.9.8/order/info/'+ auctionCheckout['orderID'], {
                      method: 'PUT',
                      headers: {
                          'Content-Type': 'application/json'
                      },
                      body: JSON.stringify(auctionCheckout)
                  })
                  .then((result) => result.json())
                  .then((data) => {
                      console.log(data)
                      sessionStorage.setItem("auctionCheckout", null)   
              });
        }
        else if(cartCheckout){
            // fetch('http://localhost:5090/handle_reservation_payment', {
            fetch('http://57.151.9.8/handle_reservation_payment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(cartCheckout)
                })
                .then((result) => result.json())
                .then((data) => {
                    console.log(data)
                    alert("Payment Successful")
                    sessionStorage.setItem("cartCheckout", null)   
            });
        }

    }
}

</script>
<script setup>

</script>
<template>
    <body>
        <div class="container-fluid h-custom">
            <div class="row d-flex justify-content-center align-items-center h-100">
                <div class="col-md-8 col-lg-6 col-xl-4 login">
                    <h2 style="margin-top: 20px; margin-bottom: 20px;text-align: center;">
                        Payment Unsuccessful <br><br>
                        <button type="submit" class="w-100 btn btn-outline-danger btn-lg"
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
        sessionStorage.setItem("auctionCheckout", null)   
        sessionStorage.setItem("cartCheckout", null)   
    }
}

</script>
<script setup>
</script>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            refunds: [],
            error: null,
            isLoading: true,
            selectedImage: null,
            displayName: null,
            isRefundUpdated: {},
            updatingRefundIDs: []
        }
    },
    methods: {
        selectImage(image) {
            this.selectedImage = image;
        },
        updateRefundStatus(refundID, status) {
            this.updatingRefundIDs.push(refundID);
            // http://127.0.0.1:5200 for local microservices http://57.151.9.8
            axios.put(`http://57.151.9.8/update_refund/${refundID}`, { 
                refundStatus: status,
                orderStatus: 'Refund ' + status.charAt(0).toUpperCase() + status.slice(1)
            })
            .then(response => {
                if (response.data.code === 200) {
                    this.updatingRefundIDs = this.updatingRefundIDs.filter(id => id !== refundID);
                    let refundIndex = this.refunds.findIndex(refund => refund.refundID === refundID);
                    if (refundIndex !== -1) {
                        let updatedRefund = { ...this.refunds[refundIndex], refundStatus: status.toLowerCase() };  // Change this line
                        this.refunds = [...this.refunds.slice(0, refundIndex), updatedRefund, ...this.refunds.slice(refundIndex + 1)];
                        console.log(`Refund status updated to ${status.charAt(0).toUpperCase() + status.slice(1)}`);
                    }
                    alert(response.data.message);
                } else {
                    alert('Failed to update refund status.');
                }
            })
            .catch(error => {
                this.updatingRefundIDs = this.updatingRefundIDs.filter(id => id !== refundID);
                console.error(error);
                alert('Failed to update refund status.');
            });
        },

    approveRefund(refundID) {
        let refund = this.refunds.find(refund => refund.refundID === refundID);
        if (refund && refund.refundStatus !== 'approved' && refund.refundStatus !== 'rejected') {
            if (confirm('Are you sure you want to approve this refund?')) {
                this.updateRefundStatus(refundID, 'approved');
            }
        }
    },

    rejectRefund(refundID) {
        let refund = this.refunds.find(refund => refund.refundID === refundID);
        if (refund && refund.refundStatus !== 'approved' && refund.refundStatus !== 'rejected') {
            if (confirm('Are you sure you want to reject this refund?')) {
                this.updateRefundStatus(refundID, 'rejected');
            }
        }
    },
         },

   
    

    async created() {
        try {
            const user = JSON.parse(sessionStorage.getItem("user"));
            console.log(user.data)
            if (user && user.data && user.data.userID) {
                this.displayName = user.data.displayName;
                let response;
                if (user.data.userType === 'Supplier') {
                    // Fetch the refunds for this supplier
                    
                    //response = await axios.get(`http://127.0.0.1:8000/api/v1/refund/supplier/${user.data.userID}`);

                    //This is using purely refund microservice port
                    response = await axios.get(`http://57.151.9.8/refund/supplier/${user.data.userID}`);
                    console.log(response)
                } 
                if (response && response.data.code === 200) {
                    this.refunds = response.data.data.refunds;
                } else {
                    this.error = response.data.message ? response.data.message : 'An error occurred.';
                }
            } else {
                this.error = 'No user ID found';
            }
        } catch (error) {
            this.error = error.message;
        } finally {
            this.isLoading = false;
        }
    }
}
</script>

<template>
    <body>
        <div class="container">
            

      
        <h1>Refund details</h1>

         <div v-if="isLoading">
            Loading...
            </div>

            <div v-else-if="error">
                No refund requests found
            </div>
        
        <br>
        

        <div class="container border content" v-for="refund in refunds" :key="refund.refundID">
            <h2>{{ displayName }}</h2>
            <h5>Order ID #{{ refund.orderID }}</h5>
            <div class="row">
                <h6 class="col text-secondary">Refund date and time: {{ refund.refund_timestamp }}</h6>
               
                <!-- hardcode payment method for now-->
                <h6 class="col text-end">Payment Method: Stripe</h6>
            </div>
           <!-- <div class="row">
                <h6 class="col text-secondary">Delivery location: Blk 123 Fish Market</h6>
                <h6 class="col text-end">Total: $60</h6>
            </div>-->

            <h5 class="pt-3">Items Ordered:</h5>
            <ul class="list-group list-group-flush ">
                <li class="list-group-item list-group-item-action">
                    <div class="row">
                        <div class="col-xl-2 col-md-4" >
                            <button type="button" data-bs-toggle="modal" data-bs-target="#imageModal" @click="selectImage(refund.pic)">
                                    <img :src="refund.pic" class="img-list" alt="...">
                                </button>
                        </div>
                        <div class="col-xl-10 col-md-8">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">
                                    Description of the spoilt fish
                                </h5>
                               <!-- <h5>$20</h5>-->
                            </div>
                            <p class="mb-1"> {{ refund.description }}</p>
                        </div>
                    </div>
                </li>
                
            </ul>
            <h5 class="pt-3">Refund Status: {{ refund.refundStatus }}</h5>

            <!--Button to approve and reject--> 

            <button class="btn btn-success" v-if="refund.refundStatus !== 'approved' && refund.refundStatus !== 'rejected' && !updatingRefundIDs.includes(refund.refundID)" @click="approveRefund(refund.refundID)">Approve</button>
            <button class="btn btn-danger" v-if="refund.refundStatus !== 'approved' && refund.refundStatus !== 'rejected' && !updatingRefundIDs.includes(refund.refundID)" @click="rejectRefund(refund.refundID)">Reject</button>
            

        </div>
        </div>



         <!-- modal to enlarge the picture -->
         <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">
                    <div class="modal-body">
                        <img :src="selectedImage" class="img-fluid" alt="...">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>


    </body>
</template>
<style scoped>
.progresses{
    display: flex;
    align-items: center;
}
.line{
    width: 120px;
    height: 6px;
    background: #63d19e;
}

.steps{
    display: flex;
    background-color: #63d19e;
    color: #fff;
    font-size: 14px;
    width: 40px;
    height: 40px;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}
.content{
    min-height: 500px;
    padding: 30px;
    overflow-y: scroll;
}
.img-list{
    height: 100px;
    width: 100px;
}
</style>
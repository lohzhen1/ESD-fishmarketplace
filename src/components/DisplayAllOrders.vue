<script setup>

</script>
<script>
import axios from 'axios';

export default {
  data() {
    return {
      orders: [],
      isLoading: true,
      error: null,
      showModal: false,
      picture: null,
      pictureUrl: '',
      description: '',
      currentOrder: null,
      stripe: null,
    };
  },
  async created() {
  
    this.getStripePublishableKey();

  try {
    const user = JSON.parse(sessionStorage.getItem("user"));
    if (user && user.data && user.data.userID) {

      //this is using the kong api gateway
     // //const response = await axios.get(`http://127.0.0.1:8000/api/v1/order/user/${user.data.userID}`);
      
      //this is using the order microservice portnumber
      // const response = await axios.get(`http://127.0.0.1:5009/order/user/${user.data.userID}`);

      const response = await axios.get(`http://57.151.9.8/order/user/${user.data.userID}`);
      if (response.data.code === 200) {
        this.orders = response.data.data.orders;
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
},

  

  methods: {
    
    toggleModal() {
      this.showModal = !this.showModal;
    },

    getStripePublishableKey() {
        fetch('http://57.151.9.8/config')
            .then((result) => result.json())
            .then((data) => {
                // Initialize Stripe.js
                this.stripe = Stripe(data.publicKey);
            });
    },

    openModal(order) {
      console.log('openModal called with order:', order);
      this.currentOrder = order;
      this.showModal = true;

    
    },

    // send the actual URL image data and encode it to base64
    onFileChange(e) {
    this.picture = e.target.files[0];
    let reader = new FileReader();
    reader.onloadend = () => {
      this.pictureUrl = reader.result;
    };
    reader.readAsDataURL(this.picture);
  },


    // Update the order status to 'Refund in progress' and create a refund. Refund button will display only if the order status is 'Completed'
    async processRefund() {
      console.log('processRefund called with currentOrder:', this.currentOrder);
    
      try {
        //check whether the current order that is selected in the modal is valid
        if (!this.currentOrder || !this.currentOrder.orderID) {
          console.error('Current order or order ID is undefined');
          return;
        }
          
        // Request a refund in the backend

        
        const refundRequestResponse = await axios.post(`http://57.151.9.8/request_refund/${this.currentOrder.orderID}`, {
        // const refundRequestResponse = await axios.post(`http://127.0.0.1:5500/request_refund/${this.currentOrder.orderID}`, {
          userID: this.currentOrder.userID,
          supplierID: this.currentOrder.supplierID,
          description: this.description,
          // Send the base64 encoded image data
          pic: this.pictureUrl.split(',')[1],  // Remove the data URL prefix
        });

        if (refundRequestResponse.data.code === 200) {
          alert('Refund requested successfully and order status updated');
          this.showModal = false; // close the modal
          this.description = ''; // reset the form
          this.pictureUrl = '';

          // Find the index of the order in the orders array
          const index = this.orders.findIndex(o => o.orderID === this.currentOrder.orderID);

          // Create a new order object with the updated status
          const updatedOrder = { ...this.currentOrder, status: 'Refunding in progress' };

          // Replace the old order with the new one in the orders array
          this.orders[index] = updatedOrder;

        } else {
          alert('An error occurred when requesting a refund: ' + refundRequestResponse.data.message);
        }
      } catch (error) {
        console.error('An error occurred:', error);
      }
    },
      //Testing the refunds in json (will delete later)
    async getAllRefunds() {
    try {
      const response = await axios.get('http://57.151.9.8/refund');

      if (response.data.code === 200) {
        console.log('All refunds:', response.data.data);
      } else {
        console.error('An error occurred:', response.data.message);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  },

  makePayment(order){
    var orderID = ""
    fetch('http://localhost:5101/handleAuctionPayment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(order)
        })
        .then((result) => result.json())
        .then((data) => {
            console.log(data.data.sessionID)
            if(data.code == "201"){
              orderID = data.data.orderID
              sessionStorage.setItem("auctionCheckout", JSON.stringify(        
                {
                  "orderID": orderID,
                  "status": "Completed",
                  "paymentMethod": "Stripe",
                  "checkoutID": data.data.sessionID
                })
              )              
              return this.stripe.redirectToCheckout({ sessionId: data.data.sessionID })
            }
          })
          .then((res) => {
              console.log(res);
              // orderResult = invoke_http(orderURL + str(order["orderID"]), method='PUT', json=updatedOrder)

          });
  }

  },
  

};
</script>

<template>


  <div class="container">
    <h2> Thank you! </h2>
  </div>

  <div class="container pb-5 mb-2">
    <div v-if="isLoading">
      Loading...
    </div>

    <div v-else-if="error">
      No orders found
    </div>

    <div v-else>
      <button @click="getAllRefunds">Get All Refunds</button>
      <div class="cart-item d-md-flex justify-content-between" v-for="(order, index) in orders" :key="index">
        <div class="px-3 my-3">
          <a class="cart-item-product">
            <div class="cart-item-product-thumb"><img src="../assets/fish.png" alt="Product"></div>
            <div class="cart-item-product-info">
              <h4 class="cart-item-product-title"></h4>
            </div>
          </a>
          <br>
        </div>

        <div class="px-3 my-3">
          <h6>Order Time: {{ order.orderedTime }}</h6>
          <h6 v-if="order.paymentMethod">Payment method: {{ order.paymentMethod }}</h6>
          <h6 v-else>Payment method: Not paid yet</h6>
          <h6>Status: {{ order.status }}</h6>
          <h6>Delivery Address: {{ order.deliveryAddress }}</h6>
          <h6><strong>Total: </strong> ${{ order.totalPrice }}</h6>
          <h6>Bought from: {{ order.supplierName }}</h6>
          <button v-if="order.status === 'Completed'" @click="openModal(order)">Refund</button>
          <button style="background-color: green;" v-if="order.status === 'Pending Payment'" @click="makePayment(order)">Make Payment</button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="showModal" class="modal">
    <div class="modal-content">
      <span class="close-button" @click="showModal = false">&times;</span>
      <p>Whats wrong with the order?</p>

      <div class="form-group">
        <label for="description">Description:</label>
        <textarea id="description" v-model="description" class="form-control"></textarea>
      </div>

      <div class="form-group">
        <label for="picture">Upload Picture:</label>
        <input type="file" id="picture" @change="onFileChange" class="form-control-file">
        <img v-if="pictureUrl" :src="pictureUrl" alt="Uploaded picture" class="uploaded-picture">
      </div>

      <button @click="processRefund">Yes, refund</button>
      <button @click="showModal = false">No, cancel</button>
    </div>
  </div>
</template>






<style scoped>

.uploaded-picture {
  display: block;
  max-width: 100%;
  height: auto;
  margin-top: 10px;
}

.modal {
  position: fixed;
  z-index: 9999;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px; /* Rounded corners */
  box-shadow: 0 2px 10px rgba(0,0,0,0.1); /* Shadow for a "lifted" effect */
  width: 80%;
  max-width: 500px;
}

.close-button {
  position: absolute;
  right: 20px;
  top: 10px;
  font-size: 30px;
  font-weight: bold;
  color: #999;
  cursor: pointer;
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  border: none;
  background-color: #007BFF;
  color: #fff;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3;
}

button:last-child {
  margin-left: 10px;
  background-color: #6c757d;
}

button:last-child:hover {
  background-color: #5a6268;
}

@media (min-width: 768px) {
  .cart-item .px-3.my-3 {
    flex-basis: 33.333%; /* Or adjust this value as needed */
  }
}
.cart-item:nth-child(even) .cart-item-product {
  justify-content: flex-end;
}

.cart-item .px-3.my-3 {
  flex-basis: 50%; /* Or adjust this value as needed */
}
.cart-items-container {
  display: flex;
  flex-wrap: wrap;
}

.total-price {
        font-size: 24px; 
    }

    body{
    margin-top:100px;
    background:#eee;
}
.product-card {
  position: relative;
  max-width: 380px;
  padding-top: 12px;
  padding-bottom: 43px;
  transition: all 0.35s;
  border: 1px solid #e7e7e7;
}
.product-card .product-head {
  padding: 0 15px 8px;
}
.product-card .product-head .badge {
  margin: 0;
}
.product-card .product-thumb {
  display: block;
}
.product-card .product-thumb > img {
  display: block;
  width: 100%;
}
.product-card .product-card-body {
  padding: 0 20px;
  text-align: center;
}
.product-card .product-meta {
  display: block;
  padding: 12px 0 2px;
  transition: color 0.25s;
  color: rgba(140, 140, 140, .75);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
}
.product-card .product-meta:hover {
  color: #8c8c8c;
}
.product-card .product-title {
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: bold;
}
.product-card .product-title > a {
  transition: color 0.3s;
  color: #343b43;
  text-decoration: none;
}
.product-card .product-title > a:hover {
  color: #ac32e4;
}
.product-card .product-price {
  display: block;
  color: #404040;
  font-family: 'Montserrat', sans-serif;
  font-weight: normal;
}
.product-card .product-price > del {
  margin-right: 6px;
  color: rgba(140, 140, 140, .75);
}
.product-card .product-buttons-wrap {
  position: absolute;
  bottom: -20px;
  left: 0;
  width: 100%;
}
.product-card .product-buttons {
  display: table;
  margin: auto;
  background-color: #fff;
  box-shadow: 0 12px 20px 1px rgba(64, 64, 64, .11);
}
.product-card .product-button {
  display: table-cell;
  position: relative;
  width: 50px;
  height: 40px;
  border-right: 1px solid rgba(231, 231, 231, .6);
}
.product-card .product-button:last-child {
  border-right: 0;
}
.product-card .product-button > a {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: all 0.3s;
  color: #404040;
  font-size: 16px;
  line-height: 40px;
  text-align: center;
  text-decoration: none;
}
.product-card .product-button > a:hover {
  background-color: #ac32e4;
  color: #fff;
}
.product-card:hover {
  border-color: transparent;
  box-shadow: 0 12px 20px 1px rgba(64, 64, 64, .09);
}
.product-category-card {
  display: block;
  max-width: 400px;
  text-align: center;
  text-decoration: none !important;
}
.product-category-card .product-category-card-thumb {
  display: table;
  width: 100%;
  box-shadow: 0 12px 20px 1px rgba(64, 64, 64, .09);
}
.product-category-card .product-category-card-body {
  padding: 20px;
  padding-bottom: 28px;
}
.product-category-card .main-img, .product-category-card .thumblist {
  display: table-cell;
  padding: 15px;
  vertical-align: middle;
}
.product-category-card .main-img > img, .product-category-card .thumblist > img {
  display: block;
  width: 100%;
}
.product-category-card .main-img {
  width: 65%;
  padding-right: 10px;
}
.product-category-card .thumblist {
  width: 35%;
  padding-left: 10px;
}
.product-category-card .thumblist > img:first-child {
  margin-bottom: 6px;
}
.product-category-card .product-category-card-meta {
  display: block;
  padding-bottom: 9px;
  color: rgba(140, 140, 140, .75);
  font-size: 11px;
  font-weight: 600;
}
.product-category-card .product-category-card-title {
  margin-bottom: 0;
  transition: color 0.3s;
  color: #343b43;
  font-size: 18px;
}
.product-category-card:hover .product-category-card-title {
  color: #ac32e4;
}
.product-gallery {
  position: relative;
  padding: 45px 15px 0;
  box-shadow: 0 12px 20px 1px rgba(64, 64, 64, .09);
}
.product-gallery .gallery-item::before {
  display: none !important;
}
.product-gallery .gallery-item::after {
  box-shadow: 0 8px 24px 0 rgba(0, 0, 0, .26);
}
.product-gallery .video-player-button, .product-gallery .badge {
  position: absolute;
  z-index: 5;
}
.product-gallery .badge {
  top: 15px;
  left: 15px;
  margin-left: 0;
}
.product-gallery .video-player-button {
  top: 0;
  right: 15px;
  width: 60px;
  height: 60px;
  line-height: 60px;
}
.product-gallery .product-thumbnails {
  display: block;
  margin: 0 -15px;
  padding: 12px;
  border-top: 1px solid #e7e7e7;
  list-style: none;
  text-align: center;
}
.product-gallery .product-thumbnails > li {
  display: inline-block;
  margin: 10px 3px;
}
.product-gallery .product-thumbnails > li > a {
  display: block;
  width: 94px;
  transition: all 0.25s;
  border: 1px solid transparent;
  background-color: #fff;
  opacity: 0.75;
}
.product-gallery .product-thumbnails > li:hover > a {
  opacity: 1;
}
.product-gallery .product-thumbnails > li.active > a {
  border-color: #ac32e4;
  cursor: default;
  opacity: 1;
}
.product-meta {
  padding-bottom: 10px;
}
.product-meta > a, .product-meta > i {
  display: inline-block;
  margin-right: 5px;
  color: rgba(140, 140, 140, .75);
  vertical-align: middle;
}
.product-meta > i {
  margin-top: 2px;
}
.product-meta > a {
  transition: color 0.25s;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}
.product-meta > a:hover {
  color: #8c8c8c;
}
.cart-item {
  position: relative;
  margin-bottom: 30px;
  padding: 0 50px 0 10px;
  background-color: #fff;
  box-shadow: 0 12px 20px 1px rgba(64, 64, 64, .09);
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.cart-item .cart-item-label {
  display: block;
  margin-bottom: 15px;
  color: #8c8c8c;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
}
.cart-item .cart-item-product {
  display: table;
  width: 420px;
  text-decoration: none;
}
.cart-item .cart-item-product-thumb, .cart-item .cart-item-product-info {
  display: table-cell;
  vertical-align: top;
}
.cart-item .cart-item-product-thumb {
  width: 110px;
}
.cart-item .cart-item-product-thumb > img {
  display: block;
  width: 100%;
}
.cart-item .cart-item-product-info {
  padding-top: 5px;
  padding-left: 15px;
}
.cart-item .cart-item-product-info > span {
  display: block;
  margin-bottom: 2px;
  color: #404040;
  font-size: 12px;
}
.cart-item .cart-item-product-title {
  margin-bottom: 8px;
  transition: color, 0.3s;
  color: #343b43;
  font-size: 16px;
  font-weight: bold;
}
.cart-item .cart-item-product:hover .cart-item-product-title {
  color: #ac32e4;
}
.cart-item .count-input {
  display: inline-block;
  width: 85px;
}
.cart-item .remove-item {
  right: -10px !important;
}
@media (max-width: 991px) {
  .cart-item {
    padding-right: 30px;
  }
  .cart-item .cart-item-product {
    width: auto;
  }
}
@media (max-width: 768px) {
  .cart-item {
    padding-right: 10px;
    padding-bottom: 15px;
  }
  .cart-item .cart-item-product {
    display: block;
    width: 100%;
    text-align: center;
  }
  .cart-item .cart-item-product-thumb, .cart-item .cart-item-product-info {
    display: block;
  }
  .cart-item .cart-item-product-thumb {
    margin: 0 auto 10px;
  }
  .cart-item .cart-item-product-info {
    padding-left: 0;
  }
  .cart-item .cart-item-label {
    margin-bottom: 8px;
  }
}
.comparison-table {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  -ms-overflow-style: -ms-autohiding-scrollbar;
}
.comparison-table table {
  min-width: 750px;
  table-layout: fixed;
}
.comparison-table .comparison-item {
  position: relative;
  margin-bottom: 10px;
  padding: 13px 12px 18px;
  background-color: #fff;
  text-align: center;
  box-shadow: 0 12px 20px 1px rgba(64, 64, 64, .09);
}
.comparison-table .comparison-item .comparison-item-thumb {
  display: block;
  width: 80px;
  margin-right: auto;
  margin-bottom: 12px;
  margin-left: auto;
}
.comparison-table .comparison-item .comparison-item-thumb > img {
  display: block;
  width: 100%;
}
.comparison-table .comparison-item .comparison-item-title {
  display: block;
  margin-bottom: 14px;
  transition: color 0.25s;
  color: #404040;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}
.comparison-table .comparison-item .comparison-item-title:hover {
  color: #ac32e4;
}
.remove-item {
  display: block;
  position: absolute;
  top: -5px;
  right: -5px;
  width: 22px;
  height: 22px;
  padding-left: 1px;
  border-radius: 50%;
  background-color: #ff5252;
  color: #fff;
  line-height: 23px;
  text-align: center;
  box-shadow: 0 3px 12px 0 rgba(255, 82, 82, .5);
  cursor: pointer;
}
.card-wrapper {
  margin: 30px -15px;
}
@media (max-width: 576px) {
  .card-wrapper .jp-card-container {
    width: 260px !important;
    
  }
  .card-wrapper .jp-card {
    min-width: 250px !important;
  }
}


</style>



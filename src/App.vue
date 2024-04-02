<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <nav class="navbar fixed-top navbar-expand-lg bg-light">
      
      <!-- Customer/visitor navbar -->
      <div class="container-fluid py-2" v-if="!user.loggedIn || user.data.userType == 'Customer'">
        <RouterLink class="navbar-brand px-3" to="/"><img src="./assets/logo.png" height="50px"/></RouterLink>
        <button class="navbar-toggler px-3" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-end px-3" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto mb-2 mb-lg-0">
            <!-- Follow the first li format -->
            <li class="nav-item">
              <RouterLink class="nav-link" aria-current="page" to="/" v-bind:class="{ 'active': $route.path == '/' }">Marketplace</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" aria-current="page" to="/auction" v-bind:class="{ 'active': $route.path == '/auction' }">Auction</RouterLink>
            </li>
            <li class="nav-item" v-if="user.loggedIn">
              <RouterLink class="nav-link" aria-current="page" to="/cart" v-bind:class="{ 'active': $route.path == '/cart' }">Cart</RouterLink>
            </li>
            <li class="nav-item" v-if="user.loggedIn">
              <RouterLink class="nav-link" aria-current="page" :to="`/displayallorders`" v-bind:class="{'active': $route.path.startsWith('/displayallorders')}">Orders</RouterLink>
            </li>
            <li class="nav-item" v-if="user.loggedIn">
              <RouterLink class="nav-link" aria-current="page" to="/accountdetails" v-bind:class="{'active': $route.path == '/accountdetails'}">Account</RouterLink>
            </li>
            <li class="nav-item" v-if="!user.loggedIn">
              <RouterLink class="nav-link" aria-current="page" to="/login" v-bind:class="{ 'active': $route.path == '/login' }">Login</RouterLink>
            </li>
            <li class="nav-item" v-else>
              <a class="nav-link" aria-current="page" @click="logout()" style="cursor: pointer;" >Logout</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Supplier navbar -->
      <div class="container-fluid py-2" v-if="user.data.userType == 'Supplier'">
        <RouterLink class="navbar-brand px-3" to="/inventory"><img src="./assets/logo.png" height="50px"/></RouterLink>
        <button class="navbar-toggler px-3" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-end px-3" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto mb-2 mb-lg-0">
            <!-- Follow the first li format -->
            <li class="nav-item">
              <RouterLink class="nav-link" aria-current="page" to="/inventory" v-bind:class="{ 'active': $route.path == '/inventory' }">Inventory</RouterLink>
            </li>
            <li class="nav-item" v-if="user.loggedIn">
              <RouterLink class="nav-link" aria-current="page" :to="`/refunddetails/${user.data.userID}`" v-bind:class="{'active': $route.path.startsWith('/refunddetails')}">Refund details</RouterLink>
            </li>

            <li class="nav-item">
              <a class="nav-link" aria-current="page" @click="logout()" style="cursor: pointer;" >Logout</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Deliveryman navbar -->
      <div class="container-fluid py-2" v-if="user.data.userType == 'Delivery'">
        <RouterLink class="navbar-brand px-3" to="/delivery"><img src="./assets/logo.png" height="50px"/></RouterLink>
        <button class="navbar-toggler px-3" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-end px-3" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto mb-2 mb-lg-0">
            <!-- Follow the first li format -->
            <li class="nav-item">
              <RouterLink class="nav-link" aria-current="page" to="/delivery" v-bind:class="{ 'active': $route.path == '/delivery' }">Delivery</RouterLink>
            </li>
            <li class="nav-item">
              <a class="nav-link" aria-current="page" @click="logout()" style="cursor: pointer;" >Logout</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>

  


  <div class="bodyContent">
    <RouterView />
  </div>
</template>

<style scoped>
 .bodyContent{ 
    padding-top: 95px; 
}

</style>
<script>
import router from './router/index'

if(JSON.parse(sessionStorage.getItem("user")) == null){
    sessionStorage.setItem("user", JSON.stringify(        
        {
            loggedIn: false,
            data: {userType: 'Visitor'}
    }))
}

export default {

    mounted() {
      document.addEventListener('login', (event) => {
        this.user = JSON.parse(sessionStorage.getItem("user"))
      });
    },
    data(){
        return{
            // user: {
            //     loggedIn: false,
            //     data: {userType: 'Visitor'}
            // }
            user: JSON.parse(sessionStorage.getItem("user"))
        }
    },
    methods: {
        logout(){
          var confirmLogout = confirm("Are you sure you want to logout?");
          if(confirmLogout){
            sessionStorage.setItem("user", JSON.stringify(        
                {
                    loggedIn: false,
                    data: {userType: 'Visitor'}
            }))
            document.dispatchEvent(new CustomEvent('login', 
              { loggedIn: false,
                data: {userType: 'Visitor'} })
            );
            alert("You've logged out")
            router.push('/')
          }
        }
    
    },
    

}
</script>
<script setup>

</script>
<template>
    <body>
        <div class="container-fluid h-custom">
            <div class="row d-flex justify-content-center align-items-center h-100">
                <div class="col-md-8 col-lg-6 col-xl-4 offset-xl-1 login">
                    <h2 style="margin-top: 20px; margin-bottom: 20px;">Login</h2>
                    <form action="#" @submit.prevent="Login">

                        <!-- Email input -->
                        <div class="form-outline mb-4">
                            <label class="form-label" for="form3Example3">Username</label>
                            <input type="text" id="form3Example3" class="form-control form-control-lg"
                            placeholder="Enter a valid username" v-model="username" required />
                        </div>

                        <!-- Password input -->
                        <div class="form-outline mb-3">
                            <label class="form-label" for="form3Example4">Password</label>
                            <input type="password" id="form3Example4" class="form-control form-control-lg"
                            placeholder="Enter password" v-model="password" required/>
                        </div>


                        <div class="text-center mt-4 pt-2">
                            <button type="submit" class="w-100 btn btn-outline-primary btn-lg"
                            style="padding-left: 2.5rem; padding-right: 2.5rem;" @click="login()"
                            >Login</button>
                        </div>

                    </form>
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
    },
    data(){
        return{
            username: '',
            password: '',
        }
    },
    methods: {
        login(){
            fetch('http://localhost:5010/user/login', {//
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        'username': this.username,
                        'password': this.password
                    })
                })
                .then((result) => result.json())
                .then((data) => {
                    if(data.code == '200'){
                        var toStore = {
                            loggedIn: true,
                            data: data.data
                        }
                        sessionStorage.setItem("user", JSON.stringify(toStore))
                        document.dispatchEvent(new CustomEvent('login', 
                            {loggedIn: true}
                        ));
                        alert("Login Successful")
                        if(data.data.userType == 'Customer'){
                            router.push({path: '/'})
                        }
                        else if(data.data.userType == 'Supplier'){
                            router.push({path: '/inventory'})
                        }
                        else{
                            router.push({path: '/delivery'})

                        }

                    }
                    else{
                        alert("Wrong username or password!")
                    }
            });
        }
    
    },
    

}
</script>
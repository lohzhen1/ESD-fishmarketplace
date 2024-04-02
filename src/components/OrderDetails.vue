<script setup>

</script>
<template>
    <body>
        <div class="container">
        <h1>Order details</h1>

        <div class="container d-flex justify-content-center align-items-center">
            <div class="progresses">
                <div class="steps">
                    <span><i class="fa fa-check"></i></span>
                </div>
                <span class="line"></span>
                <div class="steps">
                    <span><i class="fa fa-check"></i></span>
                </div>
                <span class="line"></span>
                <div class="steps">
                    <span class="font-weight-bold">3</span>
                </div>
            </div>
        </div>
        <br>
        <h5 class="text-center">Status: Delivering</h5>
        <div class="container border content">
            <h5>Order ID #123456</h5>
            <div class="row">
                <h6 class="col text-secondary">Order date: 28 Jan 2024</h6>
                <h6 class="col text-end">Payment Method: Paypal</h6>
            </div>
            <div class="row">
                <h6 class="col text-secondary">Delivery location: Blk 123 Fish Market</h6>
                <h6 class="col text-end">Total: $60</h6>
            </div>

            <h5 class="pt-3">Items Ordered:</h5>
            <ul class="list-group list-group-flush ">
                <li class="list-group-item list-group-item-action">
                    <div class="row">
                        <div class="col-xl-2 col-md-4" >
                            <img src="../assets/fish.png" class="img-list" alt="...">
                        </div>
                        <div class="col-xl-10 col-md-8">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">
                                    Fresh Fish in box
                                </h5>
                                <h5>$20</h5>
                            </div>
                            <p class="mb-1">5kg</p>
                        </div>
                    </div>
                </li>
                <li class="list-group-item list-group-item-action">
                    <div class="row">
                        <div class="col-xl-2 col-md-4" >
                            <img src="../assets/fish.png" class="img-list" alt="...">
                        </div>
                        <div class="col-xl-10 col-md-8">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">
                                    Fresh Fish in box
                                </h5>
                                <h5>$20</h5>
                            </div>
                            <p class="mb-1">5kg</p>
                        </div>
                    </div>
                </li>
                <li class="list-group-item list-group-item-action">
                    <div class="row">
                        <div class="col-xl-2 col-md-4" >
                            <img src="../assets/fish.png" class="img-list" alt="...">
                        </div>
                        <div class="col-xl-10 col-md-8">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">
                                    Fresh Fish in box
                                </h5>
                                <h5>$20</h5>
                            </div>
                            <p class="mb-1">5kg</p>
                        </div>
                    </div>
                </li>
            </ul>

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
<script setup>

</script>
<template>
    <div id="account-details">
      <h2>Account Details</h2>
      <div class="detail">
        <label>Username:</label>
        <p>{{ username }}Account test name</p>
      </div>
      <div class="detail">
        <label>Email:</label>
        <p>{{ email }}Test1234@email.com</p>
      </div>
    </div>
  </template>


<style scoped>
#account-details {
  width: 300px;
  margin: 0 auto;
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

#account-details h2 {
  text-align: center;
  color: #6c757d;
}

.detail {
  margin-top: 20px;
}

.detail label {
  font-weight: bold;
  color: #6c757d;
}

.detail p {
  margin-top: 5px;
  color: #343a40;
}

</style>
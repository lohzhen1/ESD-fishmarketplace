# FishMarketWeb

Did a Bidding system buying of fishes for restaurant and fishmonger. 

We utilized Flask for the REST API and VueJS for the frontend. We incorporated 
external API services such as Stripe for payment processing. Additionally, we 
implemented RabbitMQ as our AMQP message broker system and employed Kong 
API for API gateway load balancing.  

We utilized Docker to containerize our microservices. 

The features we developed include an Auction system, which functions as a bidding platform 
akin to a concert system. We also implemented a Queue System for purchasing fish, enabling 
users to reserve fish after displaying them to potential buyers. In cases where customers 
discover that the received fish is spoiled, they can request a refund. 

Refund requests are manually reviewed, and approval depends on the condition of the fish, as depicted in the 
pictures submitted through our website. 

Deployed Kubernetes Cluster for Spoilt Fish scenario which eases deployment and scaling of microservice containers  
Kubernetes Cluster deployed on Azure Kubernetes Service (AKS)
NGINX Ingress for routing and controlling traffic in AKS 



![image](https://github.com/lohzhen1/ESD-fishmarketplace/assets/101655111/de7f4c3d-deac-473b-814f-c360190fb9f3)


Video on how our project works:
https://www.youtube.com/watch?v=oDSGsa2g5bY






CREATE TABLE [User] (
    userID INT PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    password VARCHAR(255),
    displayName VARCHAR(100),
    userType VARCHAR(64) NOT NULL,
    deliveryAddress VARCHAR(64) NOT NULL,
    contactNum VARCHAR(64) NOT NULL,
    cartID INT,
    email VARCHAR(255) NOT NULL,

);

INSERT INTO [User] (userID, username, password, displayName, userType, deliveryAddress, contactNum, cartID, email) VALUES
(1, 'JohnDoe', 'password', 'John Doe', 'Customer', '123 Main St', '1234567890', 1, "john@gmail.com"),
(2, 'JaneDoe', 'password', 'Jane Doe', 'Customer', '456 Maple St', '0987654321', 2, "jane@gmail.com");







CREATE TABLE [Notification] (
    notifiID VARCHAR(13) PRIMARY KEY,
    userID INT NOT NULL,
    description VARCHAR(64) NOT NULL,
    notif_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES [User](userID)
);

INSERT INTO [Notification] (notifiID, userID, description) VALUES
('N1', 1, 'Your order has been shipped.'),
('N2', 2, 'Your order has been delivered.');




CREATE TABLE [Refund] (
    refundID VARCHAR(64) PRIMARY KEY,
    userID INT,
    orderID INT,
    supplierID INT,
    description VARCHAR(255),
    pic VARCHAR(255),
    refundStatus VARCHAR(64),
    refund_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES [User](userID),
    FOREIGN KEY (orderID) REFERENCES [Order](orderID),
    FOREIGN KEY (supplierID) REFERENCES [User](userID)
);


INSERT INTO [Refund] (refundID, userID, supplierID, description, pic, refundStatus, refund_timestamp)
VALUES (1, 1, 3, 'Refund for damaged goods', 'pic1.jpg', 'Pending', GETDATE());

INSERT INTO [Refund] (refundID, userID, supplierID ,description, pic, refundStatus, refund_timestamp)
VALUES (2, 2, 3, 'Refund for late delivery', 'pic2.jpg', 'Approved', GETDATE());




CREATE TABLE [Cart] (
    cartID INT PRIMARY KEY,
    userID INT,
    FOREIGN KEY (userID) REFERENCES [User](userID)
);

INSERT INTO [Cart] (cartID, userID)
VALUES (1, 1);

INSERT INTO [Cart] (cartID, userID)
VALUES (2, 2);



CREATE TABLE [Cart_Item] (
    cartItemID INT PRIMARY KEY IDENTITY(1,1),
    cartID INT,
    fishID INT,
    itemName VARCHAR(100),
    price FlOAT,
    qty INT,
    FOREIGN KEY (cartID) REFERENCES [Cart](cartID),
    FOREIGN KEY (fishID) REFERENCES [Inventory](fishID)
);

INSERT INTO [dbo].[Cart_Item] (cartID, fishID, itemName, price, qty)
VALUES (1, 1, 'Fish Item 1', 10.0, 2);

INSERT INTO [dbo].[Cart_Item] (cartID, fishID, itemName, price, qty)
VALUES (2, 2, 'Fish Item 2', 20.0, 3);

INSERT INTO [dbo].[Cart_Item] (cartID, fishID, itemName, price, qty)
VALUES (1, 3, 'Bluefin Tuna', 20.0, 3);




CREATE TABLE [Inventory] (
    fishID INT PRIMARY KEY,
    userID INT,
    itemName VARCHAR(100),
    fishImage VARCHAR(255),
    description VARCHAR(255),
    price FLOAT,
    qty INT,
    FOREIGN KEY (userID) REFERENCES [User](userID)
);

INSERT INTO [Inventory] (fishID, userID, itemName, description, price, qty)
VALUES (1, 1, 'Fish Item 1', 'Description for Fish Item 1', 10.0, 2);

INSERT INTO [Inventory] (fishID, userID, itemName, description, price, qty)
VALUES (2, 2, 'Fish Item 2', 'Description for Fish Item 2', 20.0, 3);

INSERT INTO [Inventory] (fishID, userID, itemName, description, price, qty)
VALUES (3, 1, 'Blue Fin Tuna', 'Description for Fish Item 2', 20.0, 0);

INSERT INTO [Inventory] (fishID, userID, itemName, description, price, qty)
VALUES (4, 1, 'Salmon', 'Description for Fish Item 2', 20.0, 2);

INSERT INTO [Inventory] (fishID, userID, itemName, description, price, qty)
VALUES (5, 1, 'Fish For Reserve', 'Description for Fish Item 2', 20.0, 0);



CREATE TABLE [Auction] (
    auctionID INT PRIMARY KEY,
    fishID INT,
    winnerID INT,
    winnerName VARCHAR(100),
    itemName VARCHAR(100),
    currentPrice FLOAT,
    timestart DATETIME DEFAULT GETDATE(),
    timeend DATETIME,
    status VARCHAR(50),
    FOREIGN KEY (fishID) REFERENCES [Inventory](fishID),
    FOREIGN KEY (winnerID) REFERENCES [User](userID)
);

INSERT INTO [Auction] (auctionID, fishID, winnerID, winnerName, currentPrice, status)
VALUES (1, 1, 1, 'Winner 1', 10.0, 'Active');

INSERT INTO [Auction] (auctionID, fishID, winnerID, winnerName, currentPrice, status)
VALUES (2, 2, 2, 'Winner 2', 20.0, 'Active');



CREATE TABLE [Auction_Records] (
    auctionRecordID INT PRIMARY KEY,
    auctionID INT,
    bidderID INT,
    biddingPrice FLOAT,
    FOREIGN KEY (auctionID) REFERENCES [Auction](auctionID),
    FOREIGN KEY (bidderID) REFERENCES [User](userID)
);

INSERT INTO Auction_Records (auctionRecordID, auctionID, bidderID, biddingPrice)
VALUES (1, 1, 1, 15.0);

INSERT INTO Auction_Records (auctionRecordID, auctionID, bidderID, biddingPrice)
VALUES (2, 2, 2, 25.0);

CREATE TABLE [Bidding_Records] (
    biddingRecordID INT PRIMARY KEY,
    auctionID INT,
    bidderID INT,
    biddingPrice FLOAT,
    bidTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auctionID) REFERENCES [Auction](auctionID),
    FOREIGN KEY (bidderID) REFERENCES [User](userID)
);

INSERT INTO Bidding_Records (biddingRecordID, auctionID, bidderID, biddingPrice, bidTime)
VALUES (1, 1, 1, 15.0, GETDATE());

INSERT INTO Bidding_Records (biddingRecordID, auctionID, bidderID, biddingPrice, bidTime)
VALUES (2, 2, 2, 25.0, GETDATE());


CREATE TABLE [Order] (
    orderID INT PRIMARY KEY,
    userID INT,
    supplierID INT,
    orderedTime DATETIME,
    paymentMethod VARCHAR(255),
    deliveryAddress VARCHAR(255),
    totalPrice FLOAT,
    status VARCHAR(255),
    supplierName VARCHAR(100),
    FOREIGN KEY (userID) REFERENCES [User](userID),
    FOREIGN KEY (supplierID) REFERENCES [User](userID)
);

INSERT INTO [Order] (orderID, userID, supplierID, orderedTime, paymentMethod, deliveryAddress, totalPrice, status, supplierName)
VALUES 
(1, 1, 3, '2022-01-01T00:00:00', 'Credit Card', '123 Main St', 100.00, 'Completed', 'Ah Tan Pte Ltd'),
(2, 2, 3, '2022-01-02T00:00:00', 'PayPal', '456 Oak St', 200.00, 'Completed', 'Ah Tan Pte Ltd'),
(3, 1, 3, '2022-01-01T00:00:00', 'Credit Card', '123 Main St', 100.00, 'Completed', 'Ah Tan Pte Ltd'),
(4, 2, 3, '2022-01-02T00:00:00', 'PayPal', '456 Oak St', 200.00, 'Completed', 'Ah Tan Pte Ltd'),
(5, 1, 3, '2022-01-01T00:00:00', 'Credit Card', '123 Main St', 100.00, 'Completed', 'Ah Tan Pte Ltd'),
(6, 2, 3, '2022-01-02T00:00:00', 'PayPal', '456 Oak St', 200.00, 'Completed', 'Ah Tan Pte Ltd'),
(7, 1, 3, '2022-01-01T00:00:00', 'Credit Card', '123 Main St', 100.00, 'Completed', 'Ah Tan Pte Ltd'),
(8, 2, 3, '2022-01-02T00:00:00', 'PayPal', '456 Oak St', 200.00, 'Completed', 'Ah Tan Pte Ltd'),
(11, 1, 3, CAST(GETDATE() AS DATE), 'Pay Pal', '123 Main St' , 100 , 'Completed' , 'Ah Tan Pte Ltd');



CREATE TABLE [Reservation] (
    reserveID INT PRIMARY KEY IDENTITY(1,1),
    userID INT,
    fishID INT,
    reserve_timestamp DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (userID) REFERENCES [User](userID),
    FOREIGN KEY (fishID) REFERENCES [Inventory](fishID)
);

INSERT INTO [Reservation] (userID, fishID)
VALUES (1, 1);

INSERT INTO [Reservation] (userID, fishID)
VALUES (2, 2);


#Jiawei
#View Reserve Button
INSERT INTO [dbo].[Order] (orderID, userID, supplierID, orderedTime, paymentMethod, deliveryAddress, totalPrice, status, supplierName) 
VALUES (11, 1, 3, CAST(GETDATE() AS DATE), 'Pay Pal', '123 Main St' , 100 , 'Completed' , 'Ah Tan Pte Ltd');

CREATE TABLE [Order_Details] (
    detailID INT PRIMARY KEY IDENTITY(1,1),
    orderID INT,
    fishID INT,
    qty INT,
    subTotal INT,
    FOREIGN KEY (orderID) REFERENCES [Order](orderID),
    FOREIGN KEY (fishID) REFERENCES [Inventory](fishID)
);

INSERT INTO [dbo].[Order_Details] (detailID, orderID, fishID, qty, subTotal)
VALUES (7, 9, 3, 10.0, 2);

#View Out of Stock Button



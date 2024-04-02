

--user------------------
CREATE TABLE `User` (
    userID INT PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    displayName VARCHAR(100),
    userType VARCHAR(64) NOT NULL,
    deliveryAddress VARCHAR(64) NOT NULL,
    contactNum VARCHAR(64) NOT NULL,
    password VARCHAR(255) NOT NULL
);


INSERT INTO `User` (userID, username, userType, deliveryAddress, contactNum) VALUES
(1, 'John Doe', 'Customer', '123 Main St', '1234567890'),
(2, 'Jane Doe', 'Customer', '456 Maple St', '0987654321');
----------------------------------------------


--notification------------------

CREATE TABLE Notification (
    notifiID VARCHAR(13) PRIMARY KEY,
    userID INT NOT NULL,
    description VARCHAR(64) NOT NULL,
    notif_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES `User`(userID)
);


INSERT INTO Notification (notifiID, userID, description) VALUES
('N1', 1, 'Your order has been shipped.'),
('N2', 2, 'Your order has been delivered.');
----------------------------------------------



--refund-----------------
CREATE TABLE Refund (
    refundID INT PRIMARY KEY,
    userID INT,
    description VARCHAR(255),
    pic VARCHAR(255),
    refundStatus VARCHAR(64),
    refund_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES User(userID)
);

INSERT INTO Refund (refundID, userID, description, pic, refundStatus, refund_timestamp)
VALUES (1, 1, 'Refund for damaged goods', 'pic1.jpg', 'Pending', NOW());

INSERT INTO Refund (refundID, userID, description, pic, refundStatus, refund_timestamp)
VALUES (2, 2, 'Refund for late delivery', 'pic2.jpg', 'Approved', NOW());

INSERT INTO Refund (refundID, userID, description, pic, refundStatus, refund_timestamp)
VALUES (3, 3, 'Refund for wrong item', 'pic3.jpg', 'Rejected', NOW());

----------------------------------------------

--cart-----------------------------------------


CREATE TABLE Cart (
    cartID INT PRIMARY KEY,
    userID INT,
    FOREIGN KEY (userID) REFERENCES User(userID)
);

INSERT INTO Cart (cartID, userID)
VALUES (1, 1);

INSERT INTO Cart (cartID, userID)
VALUES (2, 2);

INSERT INTO Cart (cartID, userID)
VALUES (3, 3);


----------------------------------------------



-----cart_item--------------------------------------
CREATE TABLE Cart_Item (
    cartID INT PRIMARY KEY,
    fishID INT,
    itemName VARCHAR(100),
    price DOUBLE,
    qty INT,
    FOREIGN KEY (cartID) REFERENCES Cart(cartID),
    FOREIGN KEY (fishID) REFERENCES Inventory(fishID)
);

INSERT INTO Cart_Item (cartID, fishID, itemName, price, qty)
VALUES (1, 1, 'Fish Item 1', 10.0, 2);

INSERT INTO Cart_Item (cartID, fishID, itemName, price, qty)
VALUES (2, 2, 'Fish Item 2', 20.0, 3);

INSERT INTO Cart_Item (cartID, fishID, itemName, price, qty)
VALUES (3, 3, 'Fish Item 3', 30.0, 4);

----------------------------------------------------------




------inventory--------------------------------------------

CREATE TABLE Inventory (
    fishID INT PRIMARY KEY,
    userID INT,
    itemName VARCHAR(100),
    description VARCHAR(255),
    price DOUBLE,
    qty INT,
    FOREIGN KEY (userID) REFERENCES User(userID)
);

INSERT INTO Inventory (fishID, userID, itemName, description, price, qty)
VALUES (1, 1, 'Fish Item 1', 'Description for Fish Item 1', 10.0, 2);

INSERT INTO Inventory (fishID, userID, itemName, description, price, qty)
VALUES (2, 2, 'Fish Item 2', 'Description for Fish Item 2', 20.0, 3);

INSERT INTO Inventory (fishID, userID, itemName, description, price, qty)
VALUES (3, 3, 'Fish Item 3', 'Description for Fish Item 3', 30.0, 4);
----------------------------------------------------------


-----auction-------------------------------------------------

CREATE TABLE Auction (
    auctionID INT PRIMARY KEY,
    fishID INT,
    winnerID INT,
    winnerName VARCHAR(100),
    itemName VARCHAR(100),
    currentPrice DOUBLE,
    timestart TIMESTAMP,
    timeend DATETIME,
    status VARCHAR(50),
    FOREIGN KEY (fishID) REFERENCES Inventory(fishID),
    FOREIGN KEY (winnerID) REFERENCES User(userID)
);

INSERT INTO Auction (auctionID, fishID, winnerID, winnerName, currentPrice, timestart, status)
VALUES (1, 1, 1, 'Winner 1', 10.0, CURRENT_TIMESTAMP, 'Active');

INSERT INTO Auction (auctionID, fishID, winnerID, winnerName, currentPrice, timestart, status)
VALUES (2, 2, 2, 'Winner 2', 20.0, CURRENT_TIMESTAMP, 'Active');

INSERT INTO Auction (auctionID, fishID, winnerID, winnerName, currentPrice, timestart, status)
VALUES (3, 3, 3, 'Winner 3', 30.0, CURRENT_TIMESTAMP, 'Active');

----------------------------------------------------------

--auction_records--------------------------------------------

CREATE TABLE Auction_Records (
    auctionRecordID INT PRIMARY KEY,
    auctionID INT,
    bidderID INT,
    biddingPrice DOUBLE,
    FOREIGN KEY (auctionID) REFERENCES Auction(auctionID),
    FOREIGN KEY (bidderID) REFERENCES User(userID)
);

INSERT INTO Auction_Records (auctionRecordID, auctionID, bidderID, biddingPrice)
VALUES (1, 1, 1, 15.0);

INSERT INTO Auction_Records (auctionRecordID, auctionID, bidderID, biddingPrice)
VALUES (2, 2, 2, 25.0);

INSERT INTO Auction_records (auctionRecordID, auctionID, bidderID, biddingPrice)
VALUES (3, 3, 3, 35.0);
----------------------------------------------------------



--order-----------------------------------------------------

CREATE TABLE `Order` (
    orderID INT PRIMARY KEY,
    userID INT,
    orderedTime TIMESTAMP,
    paymentMethod VARCHAR(255),
    deliveryAddress VARCHAR(255),
    totalPrice DOUBLE,
    status VARCHAR(255),
    FOREIGN KEY (userID) REFERENCES User(userID)
);

INSERT INTO `Order` (orderID, userID, orderedTime, paymentMethod, deliveryAddress, totalPrice, status)
VALUES 
(1, 1, '2022-01-01 00:00:00', 'Credit Card', '123 Main St', 100.00, 'Processing'),
(2, 2, '2022-01-02 00:00:00', 'PayPal', '456 Oak St', 200.00, 'Shipped'),
(3, 3, '2022-01-03 00:00:00', 'Debit Card', '789 Pine St', 300.00, 'Delivered');

----------------------------------------------------------




--order_details--------------------------------------------
CREATE TABLE Order_Details (
    orderID INT,
    fishID INT,
    qty INT,
    subTotal DOUBLE,
    PRIMARY KEY (orderID, fishID)
);

INSERT INTO Order_Details (orderID, fishID, qty, subTotal)
VALUES 
(1, 1, 2, 20.00),
(1, 2, 1, 10.00),
(2, 3, 3, 30.00);

------------------------------------------------------------

CREATE TABLE Reservation (
    reserveID INT PRIMARY KEY,
    userID INT,
    fishID INT,
    reserve_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES User(userID),
    FOREIGN KEY (fishID) REFERENCES Fish(fishID)
);

INSERT INTO Reservation (reserveID, userID, fishID, reserve_timestamp)
VALUES (1, 1, 1, NOW());

INSERT INTO Reservation (reserveID, userID, fishID, reserve_timestamp)
VALUES (2, 2, 2, NOW());

INSERT INTO Reservation (reserveID, userID, fishID, reserve_timestamp)
VALUES (3, 3, 3, NOW());
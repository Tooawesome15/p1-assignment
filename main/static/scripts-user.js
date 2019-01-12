/* Variables
-----------------------------*/
let lastOrderUpdateTime = null;
let orders = {};
let foodData = {};

/* Last Update Time
-----------------------------*/
function updateLastOrderUpdateTime(updateTime) {
    lastOrderUpdateTime = updateTime;
    createCookie('lastOrderUpdateTime', lastOrderUpdateTime, 1);
}

/* Refresh Orders
-----------------------------*/
function getOrders(updateTime){
    postJSON('/query', {
        'Action' : 'Orders',
        'Last Update Time' : updateTime
    },
    function(data){
        if (data['Status'] == 'Success'){
            if (data['Update Time'] != null){
                updateLastOrderUpdateTime(data['Update Time']);
            }

            newOrders = data['New Orders'];
            if (newOrders != null){
                checkUpdateOrders(newOrders, (updateTime != null));
            }
        }
    });
}

function checkUpdateOrders(newOrders, notify){
    let queryFoodIDList = [];
    let updateOrderIDList = [];
    for (let newOrder of newOrders){
        let newOrderID = newOrder['Order ID'];
        if (orders[newOrderID] == null){
            orders[newOrderID] = {
                'Status' : newOrder['Status'],
                'Food ID' : newOrder['Food ID']
            };
            // Check for Missing Food Data
            if (foodData[newOrder['Food ID']] == null){
                queryFoodIDList.push(newOrder['Food ID']);
            }
            // Notifications
            updateOrderIDList.push(newOrderID);
        } else if (orders[newOrderID]['Status'] != newOrder['Status']){
            orders[newOrderID]['Status'] = newOrder['Status'];
            // Notifications
            updateOrderIDList.push(newOrderID);
        }
    }

    getFoodData(queryFoodIDList).then(function(){
        for (let orderID of updateOrderIDList){
            order = orders[orderID];
            food = foodData[order['Food ID']];
            if (notify){
                sendNotification(order['Status'], food['Food Name'], food['Stall Name']);
            }
            if (typeof updateHTMLCurrentOrderItem === 'function'){
                updateHTMLCurrentOrderItem(orderID, order['Status'], food['Food Name'], food['Stall Name']);
            }            
        }
    });
}

/* Get Food Item Data
-----------------------------*/
async function getFoodData(foodIDList){
    if (foodIDList == null){
        return null;
    }
    await new Promise(function(resolve){
        postJSON('/query', {
            'Action' : 'Food',
            'Food ID List' : foodIDList
        },
        function(data){
            if (data['Status'] == 'Success'){
                updateFoodData(data['Food Data List']);
                resolve();
            }
        });
    });
}

function updateFoodData(newFoodDataList){
    for (let newFoodData of newFoodDataList){
        foodData[newFoodData['Food ID']] = {
            'Food Name' : newFoodData['Food Name'],
            'Stall Name' : newFoodData['Stall Name']
        };
    }
}

/* Notifications
-----------------------------*/
function sendNotification(status, foodName, stallName){
    if (status == 'Accepted') {
        new Notification(`Your Order - ${foodName} has been accepted!`);
    } else if (status == 'Ready') {
        new Notification(`Your Order - ${foodName} is ready! Pick up @ Stall - ${stallName}`);
    } else if (status == 'Rejected') {
        new Notification(`Your Order - ${foodName} has been declined.`);
    } else if (status == 'Cancelled') {
        new Notification(`Your Order - ${foodName} has been cancelled.`);
    }
}

async function requestNotification(){
    await new Promise(function(resolve){
        if (!('Notification' in window)){
            alert('This browser does not support notifications. Please use another browser.');
            resolve();   
        }
        
        if (Notification.permission == 'denied'){
            Notification.requestPermission().then(function(permission){
                resolve();
            })
        }
    });
}

function initaliseOrders(){
    lastOrderUpdateTime = readCookie('lastOrderUpdateTime');
    if (lastOrderUpdateTime != null){
        getOrders(lastOrderUpdateTime);
    }
    getOrders();
}

/* Main
-----------------------------*/
if (window.location.pathname == '/home'){
    postData('/worker', null, function(data){
        navigator.serviceWorker.register(data);
        requestNotification().then(function(){
            initaliseOrders();
        });
        console.log(data);
    });
} else {
    initaliseOrders();
}

//getOrders(readCookie('lastOrderUpdateTime'));

setInterval(function(){
    getOrders(readCookie('lastOrderUpdateTime'));
}, 5000);
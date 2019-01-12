/* Variables
-----------------------------*/
let defaultHTMLOrderHistoryItemTemplate = document.getElementById('orderHistoryItemTemplate').children[0].cloneNode(true);

let htmlCurrentOrderHistory = document.getElementById('currentOrderHistory');

let htmlOrderIDList = [];

/* HTML Order History
-----------------------------*/
function updateHTMLCurrentOrderItem(orderID, status, foodName, stallName){
    let index = htmlOrderIDList.indexOf(orderID);
    if (index == -1){
        htmlOrderIDList.push(orderID);
        let htmlOrderHistoryItem = generateHTMLOrderHistoryItem(orderID, status, foodName, stallName);
        htmlCurrentOrderHistory.appendChild(htmlOrderHistoryItem);
    } else {    
        let htmlStatus = htmlCurrentOrderHistory.getElementsByClassName('orderHistoryItem2')[index];
        htmlStatus.textContent = status;
    }

    index = htmlOrderIDList.indexOf(orderID);
    let htmlOrderHistoryItem = htmlCurrentOrderHistory.children[index];
    let htmlCross = htmlOrderHistoryItem.querySelector('i');    
    if (status == 'Requested'){
        htmlCross.setAttribute('style', 'opacity: 1;');
    } else {
        htmlCross.setAttribute('style', 'opacity: 0.2;');
    }
    
    if (status == 'Accepted'){
        let intervalID = setInterval(getOrderReadyTime(orderID), 10 * 1000);
        orders[orderID]['Interval ID'] = intervalID;
    } else {
        if (orders[orderID]['Interval ID'] != null){
            clearInterval(orders[orderID]['Interval ID']);
            orders[orderID]['Interval ID'] = null;
        }
        updateOrderReadyTime(orderID);
    }
}

/* Order History Item Template Generator
-----------------------------------------*/
function generateHTMLOrderHistoryItem(orderID, status, foodName, stallName){
    let htmlOrderHistoryItem = defaultHTMLOrderHistoryItemTemplate.cloneNode(true);
    let htmlFoodName = htmlOrderHistoryItem.getElementsByClassName('orderHistoryItem1')[0];
    let htmlStatus = htmlOrderHistoryItem.getElementsByClassName('orderHistoryItem2')[0];
    let htmlStallName = htmlOrderHistoryItem.getElementsByClassName('orderHistoryItem3')[0];
    let htmlCross = htmlOrderHistoryItem.querySelector('i');

    htmlFoodName.textContent = foodName;
    htmlStatus.textContent = status;
    htmlStallName.textContent = stallName;
    htmlCross.setAttribute('onclick', `clickCancelOrder(${orderID})`);

    return htmlOrderHistoryItem;
}

/* Order Ready Time
-----------------------------*/
function getOrderReadyTime(orderID){
    postJSON('/user/history', {
        'Action' : 'Ready Time',
        'Order ID' : orderID
    },
    function(data){
        if (data['Status'] == 'Success'){
            if (data['Ready Time'] != null){
                orders[orderID]['Ready Time'] = data['Ready Time'];
            }
            if (orders[orderID]['Ready Time'] != null){
                updateOrderReadyTime(orderID);
            }
        }
    })
}

function updateOrderReadyTime(orderID){
    let index = htmlOrderIDList.indexOf(orderID);
    let htmlReadyTime = htmlCurrentOrderHistory.getElementsByClassName('orderHistoryItem4')[index];
    let readyTime = orders[orderID]['Ready Time'];

    if (orders[orderID]['Status'] == 'Accepted'){
        htmlReadyTime.textContent = `~${Number(readyTime)} mins`;
    } else {
        htmlReadyTime.textContent = '~';
    }
}

/* Cancel Requested Food Order
-----------------------------*/
function clickCancelOrder(orderID){
    if (orders[orderID]['Status'] == 'Requested'){
        user = confirm(`Cancel Food Order - ${foodData[orders[orderID]['Food ID']]['Food Name']}?`);
        if (user){
            cancelOrder(orderID);
        }
    }
}


function cancelOrder(orderID){
    postJSON('/user/history', {
        'Action' : 'Remove',
        'Order ID' : orderID
    },
    function(data){
        if (data['Status'] == 'Success'){            
            let order = orders[orderID];
            let food = foodData[order['Food ID']];
            order['Status'] = 'Removed';
            updateHTMLCurrentOrderItem(orderID, order['Status'], food['Food Name'], food['Stall Name']);            
        }
    });    
}
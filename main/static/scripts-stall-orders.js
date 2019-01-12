/* Variables
-----------------------------*/
let defaultIncomingHTMLOrderItemTemplate = document.getElementById('incomingOrderItemTemplate').children[0].cloneNode(true);
let defaultAcceptedHTMLOrderItemTemplate = document.getElementById('acceptedOrderItemTemplate').children[0].cloneNode(true);
let defaultCompletedHTMLOrderItemTemplate = document.getElementById('completedOrderItemTemplate').children[0].cloneNode(true);

let htmlIncomingOrders = document.getElementById('operationMenuIncoming').querySelector('div');
let htmlAcceptedOrders = document.getElementById('operationMenuAccepted').querySelector('div');
let htmlCompletedOrders = document.getElementById('operationMenuCompleted').querySelector('div');

let htmlOrders = {
    'Incoming' : htmlIncomingOrders,
    'Accepted' : htmlAcceptedOrders,
    'Completed' : htmlCompletedOrders
}

let orders = {
    'Incoming' : [],
    'Accepted' : [],
    'Completed' : []
};

/* HTML Order Item Generator
-----------------------------*/
function generateIncomingHTMLOrderItem(orderItem){
    let htmlOrderItem = defaultIncomingHTMLOrderItemTemplate.cloneNode(true);

    let htmlFoodName = htmlOrderItem.querySelector('p');
    htmlFoodName.textContent = orderItem['Food Name'];

    return htmlOrderItem;
}

function generateAcceptedHTMLOrderItem(orderItem){
    let htmlOrderItem = defaultAcceptedHTMLOrderItemTemplate.cloneNode(true);

    let htmlFoodName = htmlOrderItem.querySelector('p');
    htmlFoodName.textContent = orderItem['Food Name'];

    return htmlOrderItem;
}

function generateCompletedHTMLOrderItem(orderItem){
    let htmlOrderItem = defaultCompletedHTMLOrderItemTemplate.cloneNode(true);

    let htmlFoodName = htmlOrderItem.querySelector('p');
    htmlFoodName.textContent = orderItem['Food Name'];

    return htmlOrderItem;
}

let generateHTMLOrderItems = {
    'Incoming' : generateIncomingHTMLOrderItem,
    'Accepted' : generateAcceptedHTMLOrderItem,
    'Completed' : generateCompletedHTMLOrderItem 
}

/* Retrieve & Refresh
-----------------------------*/
function refreshOrders(orderType){
    postJSON('/stall/orders', {
        'Action' : `Retrieve ${orderType}`
    },
    function(data){
        if (data['Status'] == 'Success'){
            orders[orderType] = data[orderType];
            refreshHTMLOrders(orderType);
        }
    });
}

function refreshHTMLOrders(orderType){
    let htmlTypedOrders = htmlOrders[orderType];
    let typedOrders = orders[orderType];
    let generateHTMLOrderItem = generateHTMLOrderItems[orderType];

    htmlRemoveAllChild(htmlTypedOrders);
    for (let i = 0; i < typedOrders.length; i++){
        let htmlOrderItem = generateHTMLOrderItem(typedOrders[i]);
        htmlTypedOrders.appendChild(htmlOrderItem);
    }
}

function htmlRemoveAllChild(htmlParent){
    while (htmlParent.firstChild){
        htmlParent.removeChild(htmlParent.firstChild);
    }
}

function refreshAllOrders(){
    refreshOrders('Incoming');
    refreshOrders('Accepted');
    refreshOrders('Completed');
}

/* Get HTML Food Item & Index
-----------------------------*/
function getHTMLOrderItem(button){
    let parent = button.parentNode;
    while (parent.parentNode.parentNode.className != 'operationMenuItemTemplate') {
        parent = parent.parentNode;
    }

    return parent;
}

function getHTMLOrderItemIndex(htmlOrderItem){
    let child = htmlOrderItem;
    let index = 0;
    while (child = child.previousElementSibling) {
        index++;
    }
    return index;
}

/* Click Triggers & Update
-----------------------------*/
function makeDecisionOrderItem(htmlOrderItem, decision, oldOrderType, newOrderType, generateNewOrderItem){
    if (['Accept', 'Reject'].indexOf(decision) == -1){ return null; }
    if (['Incoming', 'Accepted', 'Completed'].indexOf(oldOrderType) == -1){ return null; }
    if (['Incoming', 'Accepted', 'Completed', null].indexOf(newOrderType) == -1){ return null; }
    let index = getHTMLOrderItemIndex(htmlOrderItem);
    let oldOrders = orders[oldOrderType];
    let oldOrderItem = oldOrders[index];

    postJSON('/stall/orders', {
        'Action' : `${decision} ${oldOrderType}`,
        'Order ID' : oldOrderItem['Order ID']
    },
    function(data){
        if (data['Status'] == 'Success'){
            
            // Remove from Old HTML List
            htmlOrderItem.parentNode.removeChild(htmlOrderItem);
            // Remove from Old List
            let i = oldOrders.findIndex(orderItem => orderItem['Order ID'] == data['Order ID'])
            oldOrders.splice(i, 1);
            if (newOrderType != null && generateNewOrderItem != null){
                // Add to New HTML List
                let newOrderItem = {
                    'Food Name' : data['Food Name'],
                    'Order ID' : data['Order ID']
                }
                let newHTMLOrderItem = generateNewOrderItem(newOrderItem);
                htmlOrders[newOrderType].appendChild(newHTMLOrderItem);
                // Add to New List
                let newOrders = orders[newOrderType];
                let index2 = getHTMLOrderItemIndex(newHTMLOrderItem);
                newOrders.splice(index2, 0, newOrderItem);
            }
        }
    });
}

function clickAcceptIncoming(button){
    let htmlOrderItem = getHTMLOrderItem(button);
    acceptIncoming(htmlOrderItem);
}

function acceptIncoming(htmlOrderItem){
    makeDecisionOrderItem(htmlOrderItem, 'Accept', 'Incoming', 'Accepted', generateAcceptedHTMLOrderItem);
}

function clickRejectIncoming(button){
    let htmlOrderItem = getHTMLOrderItem(button);
    rejectIncoming(htmlOrderItem);
}

function rejectIncoming(htmlOrderItem){
    makeDecisionOrderItem(htmlOrderItem, 'Reject', 'Incoming', null, null);
}

function clickAcceptAccepted(button){
    let htmlOrderItem = getHTMLOrderItem(button);
    acceptAccepted(htmlOrderItem);
}

function acceptAccepted(htmlOrderItem){
    makeDecisionOrderItem(htmlOrderItem, 'Accept', 'Accepted', 'Completed', generateCompletedHTMLOrderItem);
}

function clickRejectAccepted(button){
    let htmlOrderItem = getHTMLOrderItem(button);
    rejectAccepted(htmlOrderItem);
}

function rejectAccepted(htmlOrderItem){
    makeDecisionOrderItem(htmlOrderItem, 'Reject', 'Accepted', null, null);
}

function clickAcceptCompleted(button){
    let htmlOrderItem = getHTMLOrderItem(button);
    acceptCompleted(htmlOrderItem);
}

function acceptCompleted(htmlOrderItem){
    makeDecisionOrderItem(htmlOrderItem, 'Accept', 'Completed', null, null);
}

function clickRejectCompleted(button){
    let htmlOrderItem = getHTMLOrderItem(button);
    rejectCompleted(htmlOrderItem);
}

function rejectCompleted(htmlOrderItem){
    makeDecisionOrderItem(htmlOrderItem, 'Reject', 'Completed', 'Accepted', generateAcceptedHTMLOrderItem);
}

refreshAllOrders();

setInterval(function(){
    refreshOrders('Incoming');
}, 2500);
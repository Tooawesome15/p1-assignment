/* Variables
-----------------------------*/
let foodList = [];

let defaultHTMLAddFoodItemTemplate = document.getElementById('foodItemAdder').cloneNode(true);
let defaultHTMLFoodItemTemplate = document.getElementById('foodItemTemplate').children[0].cloneNode(true);

let defaultAddFoodItemImage = defaultHTMLFoodItemTemplate.children[0].children[0].srcset;

/* Retrieve & Refresh
-----------------------------*/
function refreshFoodList(call_back){
    postJSON('/stall/menu', {
        'Action' : 'Retrieve',
    },
    function(data){
        if (data['Status'] == 'Success'){
            foodList = data['Food List'];
            refreshHTMLFoodList();
        } else {
            alert('Error: Unable to Get Menu');
        }
    });
}

function refreshHTMLFoodList(){
    document.getElementById('foodList').innerHTML = '';
    for (let foodItem of foodList){
        let htmlFoodItem = addNewHTMLFoodItem();
        refreshHTMLFoodItem(htmlFoodItem);
    }
}

function refreshHTMLFoodItem(htmlFoodItem){
    let index = getHTMLFoodItemIndex(htmlFoodItem);
    let foodItem = foodList[index];
    
    let inputs = getHTMLFoodItemInputs(htmlFoodItem);    
    inputs[0].value = foodItem['Food Name'];
    inputs[1].value = foodItem['Price'];
    inputs[2].value = foodItem['Calorie'];
    inputs[3].value = foodItem['Preperation Time'];

    let textarea = getHTMLFoodItemTextArea(htmlFoodItem);
    textarea.value = foodItem['Description'];

    let image = getHTMLFoodItemImage(htmlFoodItem);
    image.srcset = foodItem['Image Data'];

    let newInput = document.createElement('input');
    newInput.type = 'file';
    newInput.accept = 'image/*';
    //newInput.onchange = 'updateImagePreview(this)';
    newInput.setAttribute('onchange', 'updateImagePreview(this)')
    inputs[4].parentNode.replaceChild(newInput, inputs[4]);
}

function addNewHTMLFoodItem(){
    let htmlFoodItem = document.createElement('div');
    htmlFoodItem.innerHTML = defaultHTMLFoodItemTemplate.innerHTML;
    document.getElementById('foodList').appendChild(htmlFoodItem);
    return htmlFoodItem;
}

/* Get HTML Food Item & Index
-----------------------------*/
function getHTMLFoodItem(button){
    let parent = button.parentNode;
    while (!(parent.className == 'editFoodItem' || parent.id == 'addFoodItem')) {
        parent = parent.parentNode;
    }
    parent = parent.parentNode;

    return parent;
}

function getHTMLFoodItemIndex(htmlFoodItem){
    let child = htmlFoodItem;
    let index = 0;
    while (child = child.previousElementSibling) {
        index++;
    }
    return index;
}

/* Get HTML Data Field
-----------------------------*/
function getHTMLFoodItemInputs(htmlFoodItem){
    return htmlFoodItem.getElementsByTagName('input');
}

function getHTMLFoodItemTextArea(htmlFoodItem){
    return htmlFoodItem.children[0].children[1].children[1].children[0];
}

function getHTMLFoodItemImage(htmlFoodItem){
    return htmlFoodItem.children[0].children[0];
}

/* Toggle Edits
-----------------------------*/
function toggleFoodItemButton(htmlFoodItem, boolean) {
    if (boolean) {
        let editFoodItemDiv = htmlFoodItem.children[1].children[1].children[1].children;
        editFoodItemDiv[0].style.display = 'none';
        editFoodItemDiv[1].style.display = 'flex';
    } else {
        let editFoodItemDiv = htmlFoodItem.children[1].children[1].children[1].children;
        editFoodItemDiv[0].style.display = 'initial';
        editFoodItemDiv[1].style.display = 'none';
    }
}

function disableFoodItemInput(htmlFoodItem, boolean) {
    let inputs = getHTMLFoodItemInputs(htmlFoodItem);
    for (var i = 0; i < inputs.length; i++) {
        inputs[i].disabled = boolean;
    }

    let textarea = getHTMLFoodItemTextArea(htmlFoodItem);
    textarea.disabled = boolean;
}

function toggleFoodItemEdit(htmlFoodItem, boolean){
    toggleFoodItemButton(htmlFoodItem, boolean);
    disableFoodItemInput(htmlFoodItem, !boolean);
}

/* Manual Triggers
---------------------------------*/
function clickEditFoodItem(button) {
    let htmlFoodItem = getHTMLFoodItem(button);
    editFoodItem(htmlFoodItem);
}

function editFoodItem(htmlFoodItem){
    let htmlFoodList = htmlFoodItem.parentNode;
    for (let htmlFoodItem2 of htmlFoodList.children){
        if (htmlFoodItem != htmlFoodItem2){
            cancelEditFoodItem(htmlFoodItem2);
        }
    }
    toggleFoodItemEdit(htmlFoodItem, true);
}

function clickCancelEditFoodItem(button) {
    let htmlFoodItem = getHTMLFoodItem(button);
    cancelEditFoodItem(htmlFoodItem);
}

function cancelEditFoodItem(htmlFoodItem){
    toggleFoodItemEdit(htmlFoodItem, false);
    refreshHTMLFoodItem(htmlFoodItem);
}

function clickSaveEditFoodItem(button) {
    let htmlFoodItem = getHTMLFoodItem(button);
    saveFoodItem(htmlFoodItem);
}

function saveFoodItem(htmlFoodItem){
    toggleFoodItemEdit(htmlFoodItem, false);
    
    let index = getHTMLFoodItemIndex(htmlFoodItem);
    let foodItem = foodList[index];
    let updatedFoodItem = {};

    let inputs = getHTMLFoodItemInputs(htmlFoodItem);
    if (foodItem["Food Name"] != inputs[0].value){
        updatedFoodItem["Food Name"] = inputs[0].value;
    }
    if (foodItem["Price"] != inputs[1].value){
        updatedFoodItem['Price'] = inputs[1].value;
    }
    if (foodItem["Calorie"] != inputs[2].value){
        updatedFoodItem["Calorie"] = inputs[2].value;
    }
    if (foodItem["Preperation Time"] != inputs[3].value){
        updatedFoodItem['Preperation Time'] = inputs[3].value;
    }
    let textarea = getHTMLFoodItemTextArea(htmlFoodItem)
    if (foodItem["Description"] != textarea.value){
        updatedFoodItem["Description"] = textarea.value;
    }
    let image = getHTMLFoodItemImage(htmlFoodItem);
    if (foodItem['Image Data'] != image.srcset){
        updatedFoodItem['Image Data'] = image.srcset;
    }

    if (Object.keys(updatedFoodItem).length != 0){
        updatedFoodItem['Food ID'] = foodItem['Food ID'];
        updatedFoodItem['Action'] = 'Update';
        
        postJSON('/stall/menu', updatedFoodItem, function(data){
            index = getHTMLFoodItemIndex(htmlFoodItem);
            foodItem = foodList[index];
            if (data['Status'] == 'Success'){
                if (data['Food Name'] != null){
                    foodItem['Food Name'] = data['Food Name'];
                }
                if (data['Price'] != null){
                    foodItem['Price'] = data['Price'];
                }
                if (data['Calorie'] != null){
                    foodItem['Calorie'] = data['Calorie'];
                }
                if (data['Preperation Time'] != null){
                    foodItem['Preperation Time'] = data['Preperation Time'];
                }
                if (data['Description'] != null){
                    foodItem['Description'] = data['Description'];
                }
                if (data['Image Data'] != null){
                    foodItem['Image Data'] = data['Image Data'];
                }
            } else {
                alert(data['Error']);
            }
            refreshHTMLFoodItem(htmlFoodItem);
        });
    }
}

function clickRemoveFoodItem(button){
    let htmlFoodItem = getHTMLFoodItem(button);
    removeFoodItem(htmlFoodItem);
}

function removeFoodItem(htmlFoodItem){
    let index = getHTMLFoodItemIndex(htmlFoodItem);
    let foodItem = foodList[index];
    postJSON('/stall/menu', {
        'Action' : 'Remove',
        'Food ID' : foodItem['Food ID']
    },
    function(data){
        index = getHTMLFoodItemIndex(htmlFoodItem);
        foodItem = foodList[index];
        if (data['Status'] == 'Success'){
            htmlFoodItem.parentNode.removeChild(htmlFoodItem);
            foodList.splice(index, 1);
        } else {
            alert(data['Error']);
        }
    });
}

function clickResetAddFoodItem(button){
    let htmlFoodItem = getHTMLFoodItem(button);
    resetAddFoodItem(htmlFoodItem);
}

function resetAddFoodItem(htmlFoodItem){
    htmlFoodItem.innerHTML = defaultHTMLAddFoodItemTemplate.innerHTML;
}

function clickAddAddFoodItem(button){
    let htmlFoodItem = getHTMLFoodItem(button);
    addAddFoodItem(htmlFoodItem);
}

function addAddFoodItem(htmlFoodItem){
    let inputs = getHTMLFoodItemInputs(htmlFoodItem);
    let textarea = getHTMLFoodItemTextArea(htmlFoodItem);
    let image = getHTMLFoodItemImage(htmlFoodItem);

    postJSON('/stall/menu', {
        'Action' : 'Add',
        'Food Name' : inputs[0].value,
        'Price' : inputs[1].value,
        'Calorie' : inputs[2].value,
        'Preperation Time' : inputs[3].value,
        'Description' : textarea.value,
        'Image Data' : image.srcset == defaultAddFoodItemImage ? null : image.srcset
    },
    function(data){
        if (data['Status'] == 'Success'){
            foodList.push({
                'Food ID' : data['Food ID'],
                'Food Name' : data['Food Name'],
                'Price' : data['Price'],
                'Calorie' : data['Calorie'],
                'Preperation Time' : data['Preperation Time'],
                'Description' : data['Description'],
                'Image Data' : data['Image Data']
            });

            let newHTMLFoodItem = addNewHTMLFoodItem();
            refreshHTMLFoodItem(newHTMLFoodItem);
            resetAddFoodItem(htmlFoodItem);
        } else {
            alert(data['Error']);
        }
    });
}

function updateImagePreview(button){
    let preview = button.parentNode.parentNode.children[0].children[0];
    let uploadFile = button.files[0];
    let reader = new FileReader();

    reader.onloadend = function(){
        preview.srcset = reader.result;
    }

    if (uploadFile){
        reader.readAsDataURL(uploadFile);
    } else {
        preview.src = '';
    }
}

/* Setup
---------------------------------*/
refreshFoodList();

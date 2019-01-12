let htmlqueueTime = document.getElementById('queueTime').querySelector('p');

function clickFoodItem(food_id, food_name){
    choice = confirm(`Order 1 ${food_name}?`);
    if (choice){
        postJSON(`/order/${food_id}`, null, function(data){
            if (data['Status'] == 'Success'){
                alert(
                    'Your order has been registered successfully!\n' + 
                    'Go to Profile >> Order History to check your order.');
            } else if (data['Status'] == 'Redirect') {
                window.location.replace(data['URL']);
            } else {
                alert('Something went wrong. Your order was not registered.');
            }
        });
    }
}

function getFoodReadyTime(){
    postJSON('', {
        'Action' : 'Ready Time'
    },
    function(data){
        if (data['Status'] == 'Success'){
            htmlqueueTime.textContent += `${Math.round(parseFloat(data['Ready Time']))} mins`;
        }
    })
}

getFoodReadyTime();
/* Navigation Bar
-----------------------------*/
function openLeftNav() {    
    document.getElementById("leftNav").style.display = "flex";
    document.getElementById("leftNav").style.width = "175px";
    document.getElementById("overlay").style.display = "initial";
}

function closeLeftNav() {
    document.getElementById("leftNav").style.display = "";
    document.getElementById("leftNav").style.width = "";
    document.getElementById("overlay").style.display = "";
} 

async function postJSON(url, data, callback) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.onload = function () {
        let status = xhr.status;
        let response = xhr.responseText;
        let response_data = null;
        
        if (status >= 200 && status < 400) {
            response_data = JSON.parse(response);
        } else {
            response_data = response;
        }
        callback(response_data, status);
    }
    xhr.send(JSON.stringify(data));
}

async function postData(url, data, callback, mimetypeSend){
    let xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-type', mimetypeSend == null ? 'text/plain' : mimetypeSend);
    xhr.onload = function(){
        let status = xhr.status;
        let response = xhr.responseText;
        callback(response, status);
    }
    xhr.send(data);
}

/* Cookie
-----------------------------*/
function createCookie(name, data, expireHours){
    let json_data = JSON.stringify(data);
    let now = new Date();
    if (expireHours == null){
        expireHours = 1;
    }
    now.setHours(now.getHours() + expireHours);
    let cookie = `${name}=${json_data}; expires=${now.toUTCString()}; path=/`;
    document.cookie = cookie;
}

function readCookie(name){
    let result = document.cookie.match(`${name}=([^;]+)`);
    if (result){
        return JSON.parse(result[1]);
    } else {
        return null;
    }
}

function deleteCookie(name){
    let cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC`;
    document.cookie = cookie;
}

function deleteAllCookies(){
    for (let cookie of document.cookie.split(';')){
        deleteCookie(cookie.split('=')[0]);
    }
}
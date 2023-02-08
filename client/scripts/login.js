const loginButton = document.querySelector('.loginButton')
loginButton.addEventListener("click", sendLoginRequest)

function reqListener () {
    console.log(this.responseText)
}

function getLoginArgs() {
    const usernameInput = document.querySelector('#loginUser')
    let username = usernameInput.value

    pwdInput = document.querySelector("#loginPwd")
    let pwd = pwdInput.value
    return [username, pwd]
}

function callback(httpResp) {
    alert(httpResp)
}

function sendLoginRequest() {
    const loginArgs = getLoginArgs()
    const url = "http://127.0.0.1:5000/v1/login"
    const http = new XMLHttpRequest()
    http.onreadystatechange = function() {
        if (http.readyState == 4) {
            callback(http.status)
            callback(http.responseText)
        }
    }
    
    const data = JSON.stringify({
        "username": loginArgs[0],
        "pwd": loginArgs[1]
    })

    http.open('POST', url, true)
    http.send(data)    
}


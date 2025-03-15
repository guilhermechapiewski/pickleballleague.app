{% if dev_environment %}
var handleCredentialResponseDEV = function() {
    const devUserEmail = "gc@pickleballleague.app";
    const devUserId = "1234567890";
    
    console.log("Google Account ID (DEV): " + devUserId);
    document.getElementById('loggedin-user-email').innerHTML = devUserEmail;
    document.getElementsByClassName('loggedin-user-info')[0].style.display = 'block';
    
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() + 1);
    document.cookie = `userEmail=${devUserEmail}; expires=${expirationDate.toUTCString()}; path=/`;
    document.cookie = `userId=${devUserId}; expires=${expirationDate.toUTCString()}; path=/`;
    console.log("DEV User login information saved to cookies");
}
{% else %}
var handleCredentialResponse = function(response) {
    const responsePayload = decodeJwtResponse(response.credential);
    const userEmail = responsePayload.email;
    const userId = responsePayload.sub;

    console.log("Google Account ID: " + userId);
    document.getElementById('loggedin-user-email').innerHTML = userEmail;
    document.getElementsByClassName('loggedin-user-info')[0].style.display = 'block';
    
    // Save user info in a cookie for 30 days
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() + 30);
    document.cookie = `userEmail=${userEmail}; expires=${expirationDate.toUTCString()}; path=/`;
    document.cookie = `userId=${userId}; expires=${expirationDate.toUTCString()}; path=/`;
    console.log("User login information saved to cookies");
}
{% endif %}

var decodeJwtResponse = function(token) {
    let base64Url = token.split('.')[1];
    let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    let jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

var getUserInfoFromCookies = function() {
    const cookies = document.cookie.split('; ');
    const userEmailCookie = cookies.find(row => row.startsWith('userEmail='));
    const userIdCookie = cookies.find(row => row.startsWith('userId='));
    
    if (userEmailCookie && userIdCookie) {
        const userEmail = userEmailCookie.split('=')[1];
        const userId = userIdCookie.split('=')[1];
        return { userEmail, userId };
    }
    return null;
}

var signOut = function() {
    document.cookie = "userEmail=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "userId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.getElementsByClassName('loggedin-user-info')[0].style.display = 'none';
    document.getElementById('loggedin-user-email').innerHTML = '';
}

window.onload = function() {
    const userInfo = getUserInfoFromCookies();
    if (userInfo) {
        document.getElementById('loggedin-user-email').innerHTML = userInfo.userEmail;
        document.getElementsByClassName('loggedin-user-info')[0].style.display = 'block';
        console.log("User login information loaded from cookies");
    }
}
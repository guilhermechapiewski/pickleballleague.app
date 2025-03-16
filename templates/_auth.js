{% if dev_environment %}
var handleCredentialResponseDEV = function() {
    signIn("gc@pickleballleague.app", "1234567890");
}
{% else %}
var handleCredentialResponse = function(response) {
    const responsePayload = decodeJwtResponse(response.credential);
    signIn(responsePayload.email, responsePayload.sub);
}
{% endif %}

var signIn = function(userEmail, userGoogleId) {
    document.getElementById('user_google_id').value = userGoogleId;
    document.getElementById('user_email').value = userEmail;
    document.getElementById('auth-form').submit();
}

var decodeJwtResponse = function(token) {
    let base64Url = token.split('.')[1];
    let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    let jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

var signOut = function() {
    window.location.href = "/sign-out";
}

window.onload = function() {
    var userEmail = document.getElementById('user_email').value;
    if (userEmail) {
        document.getElementById('loggedin-user-email').innerHTML = "Logged in as:<br><span>" + userEmail + "</span>";
        document.getElementsByClassName('loggedin-user-info')[0].style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('menuButton');
    const menu = document.getElementById('userMenu');
    
    menuButton.addEventListener('click', function(e) {
        e.stopPropagation();
        menu.classList.toggle('show');
    });

    document.addEventListener('click', function(e) {
        if (!menu.contains(e.target) && !menuButton.contains(e.target)) {
            menu.classList.remove('show');
        }
    });
});
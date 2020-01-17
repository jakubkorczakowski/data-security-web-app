document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";

    let loginInput = document.getElementById("username");

    loginInput.addEventListener("change", checkLoginAvailability);

    function checkLoginAvailability() {
        let loginInput = document.getElementById("username");

        let loginPattern = /^[a-z]{3,12}$/;

        if (loginInput.value != '' && loginPattern.test(loginInput.value)) {
            let baseUrl = "/app/";
            let userUrl = baseUrl + loginInput.value;

            fetch(userUrl, {method: GET}).then(function (resp) {
                console.log(resp.status);
                if (resp.status === 404) {
                    if (document.getElementById("login_taken_error_message") != null) {
                        document.getElementById("login_taken_error_message").remove()
                    }
                    loginInput.insertAdjacentHTML("afterend", "<div id='login_taken_error_message' class='error-message'>   Taki użytkownik nie istnieje. </div>")
                    return false;
                }
                if (resp.status === 200) {
                    if (document.getElementById("login_taken_error_message") != null) {
                        document.getElementById("login_taken_error_message").remove()
                    }
                    return true;
                }
                return false;

            }).catch(function (err) {
                console.log(err);
                return false;
            });
        }
    }

});
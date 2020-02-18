document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";

    let passwordInput = document.getElementById("old-password");
    let newPasswordInput = document.getElementById("new-password");
    let newRepPasswordInput = document.getElementById("new-repeated-password");
    let changePasswordForm = document.getElementById("change-password-form");


    passwordInput.addEventListener("change", checkPasswordValidity);
    newPasswordInput.addEventListener("change", checkNewPasswordValidity);
    newRepPasswordInput.addEventListener("change", checkRepeatPasswordValidity);
    newPasswordInput.addEventListener("change", checkPasswordEntropy);


    changePasswordForm.addEventListener("submit", function (event) {
        let reqiuredFields = document.querySelectorAll('#app-form .required').length;

        let n = 0;
        for (i = 0; i < reqiuredFields; i++) {
            if (event["srcElement"][i].value !== "") {
                n++;
            }
        }

        if ((n != reqiuredFields) || !(checkPasswordValidity() && checkNewPasswordValidity() && checkRepeatPasswordValidity() && checkPasswordEntropy())) {
            event.preventDefault();
        }

    });


    function checkPasswordValidity() {
        let passwordInput = document.getElementById("old-password");
        let passwordPattern = /^.{8,40}$/;
        if (!(passwordPattern.test(passwordInput.value))) {
            if (document.getElementById("wrong_password_error_message") != null) {
                document.getElementById("wrong_password_error_message").remove();
            }
            passwordInput.insertAdjacentHTML("afterend", "<div id='wrong_password_error_message' class='text-danger'>   Hasło musi mieć co najmniej 8 znaków. </div>")
            return false;
        }
        if (document.getElementById("wrong_password_error_message") != null) {
            document.getElementById("wrong_password_error_message").remove();
        }
        return true;
    }

    function checkNewPasswordValidity() {
        let passwordInput = document.getElementById("new-password");
        let passwordPattern = /^.{8,40}$/;
        if (!(passwordPattern.test(passwordInput.value))) {
            if (document.getElementById("wrong_password_error_message") != null) {
                document.getElementById("wrong_password_error_message").remove();
            }
            passwordInput.insertAdjacentHTML("afterend", "<div id='wrong_password_error_message' class='text-danger'>   Hasło musi mieć co najmniej 8 znaków. </div>")
            return false;
        }
        if (document.getElementById("wrong_password_error_message") != null) {
            document.getElementById("wrong_password_error_message").remove();
        }
        return true;
    }

    function checkRepeatPasswordValidity() {
        let passwordInput = document.getElementById("new-password");
        let repeatPasswordInput = document.getElementById("new-repeated-password");
        if (!(passwordInput.value == repeatPasswordInput.value)) {
            if (document.getElementById("wrong_repeat_password_error_message") != null) {
                document.getElementById("wrong_repeat_password_error_message").remove();
            }
            repeatPasswordInput.insertAdjacentHTML("afterend", "<div id='wrong_repeat_password_error_message' class='text-danger'>   Hasło nie pokrywa się z podanym wcześniej. </div>")
            return false;
        }
        if (document.getElementById("wrong_repeat_password_error_message") != null) {
            document.getElementById("wrong_repeat_password_error_message").remove();
        }
        return true;
    }

    function checkPasswordEntropy() {
        let passwordInput = document.getElementById("new-password");
        let entropy = get_entropy(passwordInput.value);
        if (entropy < 50) {
            if (document.getElementById("wrong_password_entropy_message") != null) {
                document.getElementById("wrong_password_entropy_message").remove();
            }
            passwordInput.insertAdjacentHTML("afterend", "<div id='wrong_password_entropy_message' class='text-danger'>   Hasło jest za słabe. </div>")
            return false;
        } else if (entropy > 50 && entropy < 100) {
            if (document.getElementById("wrong_password_entropy_message") != null) {
                document.getElementById("wrong_password_entropy_message").remove();
            }
            passwordInput.insertAdjacentHTML("afterend", "<div id='wrong_password_entropy_message'>   Hasło jest średnie. </div>")
            return true;
        } else if (entropy > 100) {
            if (document.getElementById("wrong_password_entropy_message") != null) {
                document.getElementById("wrong_password_entropy_message").remove();
            }
            passwordInput.insertAdjacentHTML("afterend", "<div id='wrong_password_entropy_message', class='text-success'>   Hasło jest mocne. </div>")
            return true;
        }
        if (document.getElementById("wrong_password_entropy_message") != null) {
            document.getElementById("wrong_password_entropy_message").remove();
        }
        return true;
    }

    function get_entropy(password) {
        alfabet_len = 26;

        big_letters_added = false;
        signs_added = false;
        sec_signs_added = false;
        numbers_added = false;

        for (c = 0; c < password.length; c++) {
            if ((big_letters_added == false) && (password.charCodeAt(c) >= "A".charCodeAt(0) && (password.charCodeAt(c) <= "Z".charCodeAt(0)))) {
                alfabet_len += 26;
                big_letters_added = true
            }
            if ((signs_added == false) && (password.charCodeAt(c) >= " ".charCodeAt(0) && (password.charCodeAt(c) <= "/".charCodeAt(0)))) {
                alfabet_len += 16;
                signs_added = true
            }
            if ((sec_signs_added == false) && (password.charCodeAt(c) >= ":".charCodeAt(0) && (password.charCodeAt(c) <= "@".charCodeAt(0)))) {
                alfabet_len += 7;
                sec_signs_added = true
            }
            if ((numbers_added == false) && (password.charCodeAt(c) >= "0".charCodeAt(0) && (password.charCodeAt(c) <= "9".charCodeAt(0)))) {
                alfabet_len += 10;
                numbers_added = true
            }
        }

        entropy = password.length * Math.log2(alfabet_len);

        return entropy

    }


});
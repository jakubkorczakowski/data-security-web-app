document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";

    let titleInput = document.getElementById("title");
    let allowInput = document.getElementById("allowed_users");
    let noteForm = document.getElementById("note-form");


    titleInput.addEventListener("change", checkTitleAvailability);
    allowInput.addEventListener("change", checkAllowedUsersValidity);

    noteForm.addEventListener("submit", function (event) {

        if ( !(checkAllowedUsersValidity()) || !(checkTitleAvailability())) {
            event.preventDefault();
        }

    });
    

    function checkAllowedUsersValidity() {
        let allowedUsersInput = document.getElementById("allowed_users");
        let allowedUsersPattern = /^[a-z]{3,12}( [a-z]{3,12}(?= ))*( [a-z]{3,12} {0,1})*$/;
        if (!(allowedUsersPattern.test(allowedUsersInput.value) || (allowedUsersInput.value == ''))) {
            if (document.getElementById("wrong_allowed_users_error_message") != null) {
                document.getElementById("wrong_allowed_users_error_message").remove();
            }
            allowedUsersInput.insertAdjacentHTML("afterend", "<div id='wrong_allowed_users_error_message' class='text-danger'>   Lista użytkowników musi być w formacie: username username ... username</div>")
            return false;
        }
        if (document.getElementById("wrong_allowed_users_error_message") != null) {
            document.getElementById("wrong_allowed_users_error_message").remove();
        }
        return true;
    }

    function checkTitleAvailability() {
        let titleInput = document.getElementById("title");
        let titlePattern = /^[a-zA-Z0-9 _\-:()!.?'",AaĄąBbCcĆćDdEeĘęFfGgHhIiJjKkLlŁłMmNnŃńOoÓóPpRrSsŚśTtUuWwYyZzŹźŻż]*$/;
        if (!(titlePattern.test(titleInput.value))) {
            if (document.getElementById("wrong_title_error_message") != null) {
                document.getElementById("wrong_title_error_message").remove();
            }
            titleInput.insertAdjacentHTML("afterend", "<div id='wrong_title_error_message' class='text-danger'>   Błędny znak w tytule. </div>")
            return false;
        }
        if (document.getElementById("wrong_title_error_message") != null) {
            document.getElementById("wrong_title_error_message").remove();
        }
        return true;
    }

});
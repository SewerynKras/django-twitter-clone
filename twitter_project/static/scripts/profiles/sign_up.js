var CURRENT_TAB = 0;
var CACHED_NAME = "";
var CACHED_EMAIL = "";
var CACHED_EMAIL_RESULT = false;

$(function () {
    var $name = $("#id_name");
    var $name_error = $("#error-name");
    var $prev_name = $("#prev-name");
    var $email = $("#id_email");
    var $email_error = $("#error-email");
    var $prev_email = $("#prev-email");

    var $sync_email = $("#id_sync_email");
    var $person_ads = $("#id_personalize_ads");
    var $send_news = $("#id_send_news");

    var $code = $("#id_code");
    var $code_error = $("#error-code");

    var $password = $("#id_password");
    var $password_error = $("#error-password");

    var $char_count = $("#char-count");

    var $mid_signup_btn = $("#mid-signup-btn");
    var $next_btn = $("#next-btn");
    var $prev_btn = $("#prev-btn");

    var $register_btn = $("#register-btn");

    var $page_counter = $("#page-counter");


    var tabs = [$("#tab0"), $("#tab1"), $("#tab2"), $("#tab3"), $("#tab4")];

    function change_tab(num) {
        tabs[CURRENT_TAB].hide();
        tabs[num].show();

        // no previous page button on the first page
        if (num == 0)
            $prev_btn.hide();
        else
            $prev_btn.show();

        // no next page button on the last page or
        // when it's replaced by the sign up button
        if (num == 4 || num == 2)
            $next_btn.hide();
        else
            $next_btn.show();

        $prev_name.val($name.val());
        $prev_email.val($email.val());
        $page_counter.text(num + 1 + " of 5");
        CURRENT_TAB = num;
    }

    $next_btn.click(next_page);
    $mid_signup_btn.click(next_page);
    $prev_btn.click(prev_page);



    /**
     * Sends and ajax request to the /meta/ajax/check_email/
     * resource and calls the callback function on the response
     * 
     * @param {function} callback 
     */
    function check_email_AJAX(callback) {
        $.ajax({
            type: "get",
            url: "/meta/ajax/check_email/",
            data: {
                email: $email.val()
            },
            dataType: "json",
            success: function (response) {
                callback(response)
            }
        });
    }

    /**
     * Checks the $email.val() against a regular expression and
     * calls check_email_AJAX.
     * Calls the callback function with a bool value whether the email
     * is correct or not.
     * @param {function} callback 
     */
    function check_email(callback) {
        let email = $email.val();

        // avoid sending unnecessary requests by caching the address
        if (email == CACHED_EMAIL) {
            callback(CACHED_EMAIL_RESULT)
            return
        }
        CACHED_EMAIL = email;

        if (email.length == 0) {
            CACHED_EMAIL_RESULT = false;
            callback(false);
            return
        }

        let re = RegExp("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if (!re.test(email)) {
            $email_error.text("Please enter a valid email address.");
            callback(false);
            CACHED_EMAIL_RESULT = false;
            return
        }

        return check_email_AJAX(
            function (response) {
                if (response.error) {
                    $email_error.text(response.error);
                    CACHED_EMAIL_RESULT = false;
                    callback(false);
                } else {
                    $email_error.text("");
                    CACHED_EMAIL_RESULT = true;
                    callback(true);
                }
            }
        )
    }

    /**
     * Checks the $name.val() against a regular expression.
     * Returns a bool value whether the name is correct or not.
     */
    function check_name() {
        let re = RegExp("^[a-zA-Z0-9 ]+$");
        if ($name.val().length == 0) {
            $name_error.text("What's your name?");
            return false;
        }
        if (!(re.test($name.val()))) {
            $name_error.text("Please enter a valid name");
            return false;
        }
        $name_error.text("");

        return true;

    }

    // Each tab has its own function that takes care of validating data
    // on that particular tab
    // It calls the callback function with a bool value whether all
    // information is correct or not

    function check_tab0(callback) {
        check_email(function (verdict) {
            callback((verdict && check_name()))
        })
    }

    function check_tab1(callback) {
        callback(true);
    }

    function check_tab2(callback) {
        callback(true);
    }

    function check_tab3(callback) {
        // Placeholder for actual email/phone validation
        // ... maybe I'll add that at some point later
        if (!($code.val() === "1234")) {
            $code_error.val("Invalid code.");
            callback(false);
            return
        }
        $code_error.val("");
        callback(true);
    }

    function check_tab4(callback) {
        let re = RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.{8,})");
        let password = $password.val();
        if (!(re.test(password))) {
            $password_error.text("Password must be at least 8 characters long and" +
                "contain lowercase/uppercase characters and at least 1 number.")
            callback(false);
            return
        }
        $password_error.text("");
        callback(true);
    }

    var checks = [check_tab0, check_tab1, check_tab2, check_tab3, check_tab4];

    /**
     * Calls the check function corresponding to the current page.
     * If all info in correct, makes the button clickable.
     */
    function check_next_page() {
        checks[CURRENT_TAB](function (verdict) {
            if (verdict) {
                $next_btn.attr("disabled", false);
                $register_btn.attr("disabled", false);
            } else {
                $next_btn.attr("disabled", true);
                $register_btn.attr("disabled", true);
            }
        })
    }

    /**
     * Move to the next page.
     */
    function next_page() {
        if (CURRENT_TAB < 4)
            change_tab(CURRENT_TAB + 1);
        $next_btn.attr("disabled", true);
        check_next_page();
    }
    /**
     * Move to the previous page.
     */
    function prev_page() {
        if (CURRENT_TAB > 0)
            change_tab(CURRENT_TAB - 1);
        $next_btn.attr('disabled', true);
        check_next_page();
    }


    $name.on("input", function () {
        $char_count.text($(this).val().length);
        check_next_page();
    })

    $email.on("input", function () {
        check_next_page();
    })

    $prev_name.on("focus", function () {
        change_tab(0);
        $name.focus();
    })

    $prev_email.on("focus", function () {
        change_tab(0);
        $email.focus();
    })

    $code.on("input", function () {
        check_next_page();
    })

    $password.on("input", function () {
        check_next_page();
    })

    $register_btn.one("click", complete_registration)

    /**
     * Sends the final AJAX request to the server.
     * This should be called only once and with correct information.
     */
    function complete_registration() {
        $.ajax({
            type: "post",
            url: "/meta/ajax/register/",
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken')
            },
            data: {
                name: $prev_name.val(),
                email: $prev_email.val(),
                password: $password.val(),
                sync_email: $sync_email.is(':checked'),
                person_ads: $person_ads.is(':checked'),
                send_news: $send_news.is(':checked')
            },
            dataType: "json",
            success: function () {
                window.location.replace("/home");
            },
            error: function (response) {
                alert("Error while processing your request, please try again later.");
                console.log(response);
            }
        });
    }

    // Setup the default tab (0)
    change_tab(0);
});
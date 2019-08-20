// VARIABLES

var $email_first = $("#id_email_first");
var $email_verify = $("#id_email_verify");
var $name_first = $("#id_name_first");
var $name_verify = $("#id_name_verify");
var $first_button = $("#first_button");
var $register_button = $("#register_button");
var EMAIL_FIRST_CORRECT = false;
var NAME_FIRST_CORRECT = false;


// GENERAL

function change_tab(num) {
    var tabname = "#tab" + num;
    $(tabname).tab("show");
    $("#current-page").text(num + " of 5");

    // change these on every tab change just in case
    $name_first.val($name_first.val());
    $email_verify.val($email_first.val());
}

$(".tab-content a").click(function () {
    change_tab($(this).attr("lead-to"));
});

$(document).ready(function () {
    $("input").addClass("form-control")

    $("#char_count").text("0/50")
    $("#id_name_first").attr("maxlength", "50")

    $("#tab1").tab("show");
});


$("#id_name_verify").focus(function (e) {
    e.preventDefault();
    change_tab(1);
    $("id_name_first").focus()
});
$("#id_email_verify").focus(function (e) {
    e.preventDefault();
    change_tab(1);
    $("id_email_first").focus()
});


// PART 1

function check_button_part1() {
    if (EMAIL_FIRST_CORRECT && NAME_FIRST_CORRECT)
        $first_button.removeClass("disabled");
    else
        $first_button.addClass("disabled");
}

$("#id_name_first").keyup(function () {
    NAME_FIRST_CORRECT = false;
    var len = $(this).val().length;
    $("#char_count").text(len + "/50");
    console.log(len)
    if (len > 0)
        NAME_FIRST_CORRECT = true;
    check_button_part1()
});


$email_first.change(function () {
    EMAIL_FIRST_CORRECT = false;
    // $(this).removeClass("is-invalid");
    // $('a').addClass('disabled');
    var email = $(this).val();
    $.ajax({
        url: "/ajax/check_email/",
        data: {
            "email": email
        },
        dataType: "json",
        success: function (response) {
            var error = response.error
            $("#error_email_first").text(error);
            if (error) {
                $email_first.addClass("is-invalid");
            } else {
                $email_first.removeClass("is-invalid");
                EMAIL_FIRST_CORRECT = true;
            }
            check_button_part1()
        }
    });
});


// PART 5

$("#id_password").keyup(function () {
    $register_button.prop("disabled", true)
    var re = RegExp("^(?=.{10,})(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])");
    var password = $(this).val();
    var $error_msg = $("#error_password");
    if (re.test(password)) {
        $error_msg.text("");
        $register_button.prop('disabled', false);
    } else
        $error_msg.text("Password must contain at least 10 lowercase" +
            " and uppercase characters and at least 1 number")
});
var $email_first = "#id_email_first";


$($email_first).change(function () {
    $(this).removeClass("is-invalid");
    $('a').addClass('disabled');
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
                $($email_first).addClass("is-invalid");
            } else
                $('a').removeClass('disabled');
        }
    });
});
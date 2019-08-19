function change_tab(num) {
    var tabname = "#tab" + num;
    $(tabname).tab("show");
    $("#current-page").text(num + " of 5");

    // change these on every tab change just in case
    $("#id_email_verify").val($("#id_email_first").val());
    $("#id_name_verify").val($("#id_name_first").val());
}


$(document).ready(function () {
    $(".nav-tabs a").click(function () {
        $(this).tab('show');
    });
    $(".tab-content a").click(function () {
        change_tab($(this).attr("lead-to"));
    });

    $("#tab1").tab("show");
    $("input").addClass("form-control")
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

    $("#char_count").text("0/50")
    $("#id_name_first").attr("maxlength", "50")
});


$("#id_name_first").keyup(function () {
    var len = $(this).val().length;
    $("#char_count").text(len + "/50");
});

//TODO: 
// code validation
// password validation
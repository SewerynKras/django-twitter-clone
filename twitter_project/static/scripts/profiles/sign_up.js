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

    $(".lead_to_1").click(function () {
        change_tab(1);
    });
    $(".lead_to_2").click(function () {
        change_tab(2);
    });
    $(".lead_to_3").click(function () {
        change_tab(3);
    });
    $(".lead_to_4").click(function () {
        change_tab(4);
    });
    $(".lead_to_5").click(function () {
        change_tab(5);
    });

    $("#tab1").tab("show");
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
})
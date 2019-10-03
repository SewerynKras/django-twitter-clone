var $main_body;
var $left_body
var $right_body;

function replace_main_body($item) {
    $main_body.html($item);
}

function hide_right_body() {
    $right_body.hide();
    $main_body.removeClass("shrink-r");
}

function show_right_body() {
    $right_body.show();
    $main_body.addClass("shrink-r");
}

function hide_left_body() {
    $left_body.hide();
    $main_body.removeClass("shrink-l");
}

function show_left_body() {
    $left_body.show();
    $main_body.addClass("shrink-l");
}

$(document).ready(function () {
    $main_body = $("#main-body")
    $left_body = $("#left-body")
    $right_body = $("#right-body")
});
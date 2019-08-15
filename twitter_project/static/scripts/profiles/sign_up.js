$(document).ready(function () {
    $("#SIGNUP_PART1_TAB").removeClass("not-yet")
    $("#SIGNUP_PART1_TAB").tab("show")
});

$("#CONTENT_1_TO_2").click(function () {
    $("#SIGNUP_PART2_TAB").tab("show")
})
$("#CONTENT_2_TO_1").click(function () {
    $("#SIGNUP_PART1_TAB").tab("show")
})
$("#CONTENT_2_TO_3").click(function () {
    $("#SIGNUP_PART3_TAB").tab("show")
})
$("#CONTENT_3_TO_2").click(function () {
    $("#SIGNUP_PART2_TAB").tab("show")
})
$("#CONTENT_3_TO_4").click(function () {
    $("#SIGNUP_PART4_TAB").tab("show")
})
$("#CONTENT_4_TO_3").click(function () {
    $("#SIGNUP_PART3_TAB").tab("show")
})
$("#CONTENT_4_TO_5").click(function () {
    $("#SIGNUP_PART5_TAB").tab("show")
})
$("#CONTENT_5_TO_4").click(function () {
    $("#SIGNUP_PART4_TAB").tab("show")
})
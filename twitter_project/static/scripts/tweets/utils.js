var $main_body;
var $left_body
var $right_body;
var CURRENT_STATE = "home";

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

function change_url(new_state, new_url) {
    history.pushState({
        state: CURRENT_STATE
    }, "", new_url)
    CURRENT_STATE = new_state;
}

function show_home() {
    // change_url("home", "/home/")
    show_left_body();
    show_right_body();
    $main_body.empty();
    load_new_tweet_form();
    load_tweet_list();
}

/**
 * Rearranges all images inside the given container so the overall
 * height and width doesn't change.
 * @param {Jquery selector} $images 
 */
function rearrange_images($images) {
    // images should be cascaded down before
    // calling this function

    // find the left and right container
    var $image_cont_left = $images.find(".tweet-image-cont-left");
    var $image_cont_right = $images.find(".tweet-image-cont-right");

    // find all image containers
    var $image1_cont = $image_cont_left.find("[image-num='1']");
    var $image3_cont = $image_cont_left.find("[image-num='3']");
    var $image2_cont = $image_cont_right.find("[image-num='2']");
    var $image4_cont = $image_cont_right.find("[image-num='4']");

    // by default all images will have
    // 50% height and width like so:

    // ------------------
    // |       |        |
    // |   1   |   2    |
    // |       |        |
    // --------|---------
    // |       |        |
    // |   3   |   4    |
    // |       |        |
    // ------------------
    $image1_cont.removeClass("tall");
    $image2_cont.removeClass("tall");
    $image3_cont.removeClass("tall");
    $image4_cont.removeClass("tall");

    $image_cont_left.removeClass("wide");
    $image_cont_left.show();
    $image_cont_right.removeClass("narrow");
    $image_cont_right.show();
    $images.show();

    // if there is no fourth image the second one
    // should have its height changed to 100% like so:
    // ------------------
    // |       |        |
    // |   1   |        |
    // |       |        |
    // --------|   2    |
    // |       |        |
    // |   3   |        |
    // |       |        |
    // ------------------
    if (!$image4_cont.is(":visible"))
        $image2_cont.addClass("tall");

    // if there is no third image the first one
    // should have its height changed to 100% like so:
    // ------------------
    // |       |        |
    // |       |        |
    // |       |        |
    // |   1   |   2    |
    // |       |        |
    // |       |        |
    // |       |        |
    // ------------------
    if (!$image3_cont.is(":visible"))
        $image1_cont.addClass("tall");

    // if there is no second image the first one
    // should have its width changed to 100% like so:
    // ------------------
    // |                |
    // |                |
    // |                |
    // |       1        |
    // |                |
    // |                |
    // |                |
    // ------------------
    if (!$image2_cont.is(":visible")) {
        $image_cont_left.addClass("wide");
        $image_cont_right.addClass("narrow");
        $image1_cont.addClass("tall");
    }

    // hide the media element if there are no images
    if (!$image1_cont.is(":visible"))
        $images.hide();
}
$(document).ready(function () {
    $main_body = $("#main-body")
    $left_body = $("#left-body")
    $right_body = $("#right-body")

    window.onpopstate = function (event) {
        if (event.state) {
            if (event.state.state == "home") {
                show_home()
            }
        }
    };
});
var $main_body;
var $left_body
var $right_body;
var $cover;

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

function change_url(state, url, push_state) {
    if (push_state)
        history.pushState(state, "", url)
    else
        history.replaceState(state, "", url)
}

function show_home(push_state = true) {
    show_left_body();
    show_right_body();
    $main_body.empty();
    load_new_tweet_form(function ($form) {
        $main_body.html($form);
    });
    load_tweet_list(function ($list) {
        $main_body.append($list)
    });
    change_url({
        state: "home"
    }, "/home", push_state);
}

function show_single_tweet(tweet_id, author, push_state = true) {
    show_left_body();
    show_right_body();
    $main_body.empty();
    load_single_tweet(tweet_id)
    change_url({
        state: "tweet",
        tweet_id: tweet_id,
        author: author
    }, `/${author}/status/${tweet_id}`, push_state);
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
    if (!$image4_cont.find("img").attr("src"))
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
    if (!$image3_cont.find("img").attr("src"))
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
    if (!$image2_cont.find("img").attr("src")) {
        $image_cont_left.addClass("wide");
        $image_cont_right.addClass("narrow");
        $image1_cont.addClass("tall");
    }

    // hide the media element if there are no images
    if (!$image1_cont.find("img").attr("src"))
        $images.hide();
}
$(document).ready(function () {
    $main_body = $("#main-body");
    $left_body = $("#left-body");
    $right_body = $("#right-body");
    $cover = $("#cover");

    window.onpopstate = function (event) {
        if (event.state) {
            if (event.state.state == "home") {
                show_home(push_state = false);
            } else if (event.state.state == "tweet") {
                show_single_tweet(event.state.tweet_id,
                    event.state.author,
                    push_state = false);
            }
        }
    };
});
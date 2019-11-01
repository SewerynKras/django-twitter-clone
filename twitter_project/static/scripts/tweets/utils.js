var $main_body;
var $left_body
var $right_body;
var $cover;
var $header;
var $header_text;
var $reply_form;
var $reply_form_preview;
var $reply_form_name;
var $reply_form_new_tweet;
var $gif_selector;
var FIRST_TWEET;
var LAST_TWEET;
var PROFILE;


/**
 * Changes the background-image css property to the url in
 * the 'thumb_url' attribute
 */
function set_gif_thumb() {
    $(this).css("background-image", `url(${$(this).attr("thumb-url")})`);
}

/**
 * Changes the background-image css property to the url in
 * the 'gif-url' attribute
 */
function set_gif_url() {
    $(this).css("background-image", `url(${$(this).attr("gif-url")})`);
}

function hide_right_body() {
    $right_body.hide();
}

function show_right_body() {
    $right_body.show();
}

function hide_left_body() {
    $left_body.hide();
}

function show_left_body() {
    $left_body.show();
}

function change_url(state, url, push_state) {
    if (push_state)
        history.pushState(state, "", url)
    else
        history.replaceState(state, "", url)
}

/**
 * Every time the user scrolls check if the last tweet is visible,
 * if so query and append more tweets to the list
 * (infinite scrolling)
 */
function check_last_tweet() {
    if (!LAST_TWEET)
        return

    if (window.scrollY >= LAST_TWEET.offset().top - $(window).height()) {
        append_tweets_to_main();
    }
}
$(document).on("scroll", check_last_tweet)

/**
 * Every couple seconds check if the user is at the top of the tweet list
 * (aka looking at the first tweet)
 * if so query and prepend newer tweets to the list
 */
function check_first_tweet() {
    if (!FIRST_TWEET)
        return

    if (window.scrollY >= FIRST_TWEET.offset().top - $(window).height()) {
        prepend_tweets_to_main();
    }
}
// 5 seconds
window.setInterval(check_first_tweet, 5000);


function reset_scroll_states() {
    LAST_TWEET = null;
    FIRST_TWEET = null;
}

/**
 * Loads and appends a list of tweets based on the current cached LAST_TWEET
 * @param {bool} set_first if true the first element of the list will be cached 
 * as FIRST_TWEET (useful if this call creates the initial list)
 */
function append_tweets_to_main(set_first = false) {
    load_tweet_list(function ($list) {
        $main_body_contents.append($list)
        LAST_TWEET = $list.eq(-1).find(".tweet-container");
        if (set_first)
            FIRST_TWEET = $list.eq(0).find(".tweet-container");
    }, PROFILE, LAST_TWEET, null);
    LAST_TWEET = null;
}

/**
 * Loads and prepends a list of tweets based on the current cached FIRST_TWEET
 */
function prepend_tweets_to_main() {
    load_tweet_list(function ($list) {
        if ($list.length) {
            $list.insertBefore(FIRST_TWEET);
            FIRST_TWEET = $list.eq(0).find(".tweet-container");
        }
    }, PROFILE, null, FIRST_TWEET);
}


function show_home(push_state = true) {
    show_left_body();
    show_right_body();
    reset_scroll_states()
    $main_body_contents.empty();
    load_new_tweet_form(function ($form) {
        $main_body_contents.html($form);
    });
    append_tweets_to_main(true);
    change_url({
        state: "home"
    }, "/home", push_state);
    $header_text.text("Latest Tweets");
}

function show_single_tweet(tweet_id, author, push_state = true) {
    show_left_body();
    show_right_body();
    reset_scroll_states()
    $main_body_contents.empty();
    PROFILE = author;
    load_single_tweet(tweet_id, function ($tweet, $comments) {
        $main_body_contents.html($tweet);
        $main_body_contents.append($comments);
    })
    change_url({
        state: "tweet",
        tweet_id: tweet_id,
        author: author
    }, `/${author}/status/${tweet_id}`, push_state);
    $header_text.text("Thread");
}

function show_reply_form(tweet_id, push_state = true) {
    $cover.show();
    $reply_form.show();
    load_single_tweet(tweet_id,
        function ($tweet) {
            $reply_form_preview.html($tweet);
            $reply_form_name.text(
                "@" + $tweet.find(".tweet-container").attr("author-username"));
        }, true) // minified = true

    load_new_tweet_form(function ($form) {
        $reply_form_new_tweet.html($form);
    }, tweet_id)

    change_url({
        state: "reply",
        tweet_id: tweet_id,
    }, "/compose/tweet", push_state);
}

function show_retweet_form(tweet_id, push_state = true) {
    $cover.show();
    $reply_form.show();
    load_new_tweet_form(function ($form) {
        $reply_form.html($form)
    }, "", tweet_id)

    change_url({
        state: "retweet",
        tweet_id: tweet_id,
    }, "/compose/tweet", push_state);
}


function show_profile(profile_id, push_state = false) {
    show_left_body();
    show_right_body();
    reset_scroll_states()
    $main_body_contents.empty();
    load_profile(profile_id, function ($profile) {
        $main_body_contents.html($profile);
    })
    append_tweets_to_main();
    change_url({
        state: "profile",
        profile_id: profile_id,
    }, `/${profile_id}`, push_state);
    $header_text.text(profile_id)
}


function hide_all_cover() {
    $reply_form.hide();
    $gif_selector.hide();
    $cover.hide();
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

/**
 * Displays the gif selector.
 */
function show_gif_selector() {
    $cover.show();
    $gif_selector.show();
}


/**
 * This will be called every time the window is resized or an AJAX call
 * is finished
 */
function resize_elements() {
    $header.width($main_body.width());
}

$(document).ready(function () {

    $main_body = $("#main-body");
    $main_body_contents = $main_body.find("#main-body-contents");
    $left_body = $("#left-body");
    $right_body = $("#right-body");
    $header = $("#header");
    $header_text = $header.find(("#header-text"));

    $cover = $("#cover");

    $gif_selector = $("#gif-selector");

    $reply_form = $("#reply-form");
    $reply_form_preview = $reply_form.find("#reply-preview");
    $reply_form_name = $reply_form.find(".tweet-reply-clickable-name");
    $reply_form_new_tweet = $reply_form.find("#reply-new");

    $(window).resize(function (e) {
        resize_elements()
    })
    $(document).ajaxComplete(function () {
        resize_elements()
    });
    $cover.click(hide_all_cover);

    // setup navigation 
    let $nav = $left_body.find(".nav");

    $nav.find("#nav-to-home").click(function (e) {
        show_home(true);
    })
    $nav.find("#nav-to-profile").click(function (e) {
        let profile_id = $(this).find("img").attr("username");
        show_profile(profile_id, true);
    })


    resize_elements();
    window.onpopstate = function (event) {
        if (event.state) {
            hide_all_cover();
            if (event.state.state == "home") {
                show_home(false);
            } else if (event.state.state == "tweet") {
                show_single_tweet(event.state.tweet_id,
                    event.state.author,
                    false);
            } else if (event.state.state == "reply") {
                show_reply_form(event.state.tweet_id, false);
            } else if (event.state.state == "retweet") {
                show_retweet_form(event.state.tweet_id, false);
            } else if (event.state.state == "profile") {
                show_profile(event.state.profile_id, false);
            }
        }
    };
});
/**
 * Converts the UTC timestamp to time elapsed
 */
function fix_timestamp() {
    var tweet_time = $(this).attr("utc"); // in seconds
    var curr_time = Math.floor(new Date().getTime() / 1000); // in seconds
    var diff = curr_time - tweet_time;
    var display = NaN;

    if (diff < 60)
        // show seconds if less than a minute passed
        display = diff + "s"
    else if (diff < 60 * 60)
        // show minutes if less than an hour passed
        display = Math.floor(diff / 60) + "m";
    else if (diff < 60 * 60 * 24)
        // show hours if less than a day passed
        display = Math.floor(diff / 60 / 60) + "h";
    else if (diff < 60 * 60 * 24 * 365) {
        // show the day and month if less than a year has passed
        var date = new Date(tweet_time * 1000);
        var day = date.getDate();
        var month = date.toLocaleString('default', {
            month: 'short'
        }); // this way month is represented with a short str ("Mar", "Oct" etc)
        display = month + " " + day;
    } else {
        // show the day, month and year
        var date = new Date(tweet_time * 1000);
        var day = date.getDate();
        var month = date.toLocaleString('default', {
            month: 'short'
        }); // this way month is represented with a short str ("Mar", "Oct" etc)
        var year = date.getFullYear();
        display = month + " " + day + ", " + year;
    }
    $(this).text(display);
}
/**
 * Sends an AJAX request to create a new Like object, updates
 * the amount of like a tweet has by 1
 */
function like_tweet() {
    var $btn = $(this);
    var tweet_id = $(this).closest("li").attr("tweet-id");
    var $num_counter = $(this).children('.tweet-likes-num').eq(0);
    var num_likes = $num_counter.text()

    $.ajax({
        url: "ajax/like_tweet/",
        data: {
            "tweet_id": tweet_id
        },
        dataType: "json",
        success: function (response) {
            if (response.liked == true) {
                num_likes = 1 + +num_likes;
                $btn.addClass("is-liked");
            } else {
                num_likes = -1 + +num_likes;
                $btn.removeClass("is-liked");
            }
            $num_counter.text(num_likes);
            $btn.one("click", like_tweet);
        }
    });
}

/**
 * Sends an AJAX GET request and appends the tweet list with received elements
 */
function get_tweets() {
    var $tweet_list = $("#tweet-list");
    $.ajax({
        url: "ajax/get_tweets/",
        dataType: "html",
        success: function (response) {
            new_tweet_list = $($.parseHTML(response)).find("li");
            $tweet_list.prepend(new_tweet_list);
            setup_tweet_list(new_tweet_list);
        }
    });
}
/**
 * Parses the .tweet-text with twemoji
 */
function parse_twemoji() {
    let text = $(this).children(".tweet-text");
    twemoji.parse(text[0])
}

function setup_tweet_list($tweets) {

    let $media = $tweets.children(".tweet-media");
    $media.each(function () {
        rearrange_images($(this));
    })

    // Convert each tweets emoji into twemojis
    $tweets.each(parse_twemoji);

    // make like button clickable
    // NOTE: I'm using one() instead of click() to
    // prevent the user from sending multiple requests in
    // a very short time, the like_tweet function will rebind
    // itself to the button once the request finishes
    let $like_btn = $tweets.children(".like-btn");
    $like_btn.one("click", like_tweet);

    // Convert dates to time elapsed
    let dates = $tweets.children(".tweet-date");
    dates.each(fix_timestamp);
}

$(document).ready(function () {
    get_tweets();

    // Change all dates from UNIX timestamps to user-readable timestamps
    $(".tweet-date").each(fix_timestamp)

    // update the timestamps every couple seconds
    setInterval(function () {
        $(".tweet-date").each(fix_timestamp)
    }, 5000);

});
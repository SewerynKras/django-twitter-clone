$(document).ready(function () {
    // Change all dates from UNIX timestamps to user-readable timestamps
    $(".tweet-date").each(fix_timestamp)
    // update the timestamps every couple seconds
    setInterval(function () {
        $(".tweet-date").each(fix_timestamp)
    }, 5000);

    // since tweets support whitespace characters they
    // need to be updated
    $(".tweet-text").each(fix_text)

    // make like button clickable
    // NOTE: I'm using one() instead of click() to
    // prevent the user from sending multiple requests in
    // a very short time, the like_tweet function will rebind
    // itself to the button once the request finishes
    $(".like-btn").one("click", like_tweet)
});

function fix_text() {
    $(this).html($(this).text())
}


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

function like_tweet(e) {
    e.preventDefault();

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
                num_likes = 1 + +num_likes
                $btn.addClass("is-liked")
            } else {
                num_likes = -1 + +num_likes
                $btn.removeClass("is-liked")
            }
            $num_counter.text(num_likes)
            $btn.one("click", like_tweet)
        }
    });
}
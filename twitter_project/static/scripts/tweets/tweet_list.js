/**
 * Converts the UTC timestamp to time elapsed
 */
function fix_tweet_timestamp() {
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
 * Converts the UTC timestamp to time elapsed
 */
function fix_poll_timestamp() {
    var poll_time = $(this).attr("end-date"); // in seconds
    var curr_time = Math.floor(new Date().getTime() / 1000); // in seconds
    var diff = poll_time - curr_time;
    var display = "Time left: ";

    if (diff < 0)
        display = "This poll is over";
    else if (diff < 60)
        // show seconds if less than a minute is left
        display += diff + "s"
    else if (diff < 60 * 60)
        // show minutes if less than an hour is left
        display += Math.floor(diff / 60) + "m";
    else if (diff < 60 * 60 * 24)
        // show hours if less than a day is left
        display += Math.floor(diff / 60 / 60) + "h";
    else
        // show days
        display += Math.floor(diff / 60 / 60 / 24) + "d";

    $(this).text(display);
}

/**
 * Make the Tweets like button send an AJAX request to create a new Like,
 * Updates the like counter.
 */
function set_like_btns() {
    var $tweet = $(this);
    var $btn = $tweet.find(".like-btn");
    var $counter = $tweet.find(".tweet-likes-num");

    $btn.one("click", function () {
        like_tweet_AJAX($tweet, $btn, $counter);
    })
}

/**
 * Sends an AJAX request to create a new Like object, updates
 * the amount of like a tweet has by 1
 */
function like_tweet_AJAX($tweet, $btn, $counter) {
    var num_likes = $counter.text();
    var tweet_id = $tweet.attr("tweet-id")
    $.ajax({
        url: "/ajax/like_tweet/",
        data: {
            "tweet_id": tweet_id
        },
        type: "post",
        dataType: "json",
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        success: function (response) {
            if (response.liked == true) {
                num_likes = 1 + +num_likes;
                $btn.addClass("is-liked");
            } else {
                num_likes = -1 + +num_likes;
                $btn.removeClass("is-liked");
            }
            $counter.text(num_likes);
            $btn.one("click", function () {
                like_tweet_AJAX($tweet, $btn, $counter);
            })
        }
    });
}

/**
 * Parses the .tweet-text with twemoji
 */
function parse_twemoji() {
    let text = $(this).children(".tweet-text");
    if (text[0])
        twemoji.parse(text[0]);
}

/**
 * Shows the media element and 
 */
function setup_gif() {
    $(this).show();
    let img = $(this).find("img");
    img.attr("src", img.attr("gif-url"));
}

function setup_tweet_list($tweets) {
    $tweets.each(setup_single_tweet)
    $tweets.one('click', function () {
        let id = $(this).attr("tweet-id")
        let author = $(this).attr("author-username")
        show_single_tweet(id, author, push_state = true)
    })
}

function set_comment_btns() {
    var $tweet = $(this);
    var $btn = $tweet.find(".comment-btn");
    var $counter = $tweet.find(".tweet-comments-num");

    $btn.click(function (e) {
        e.preventDefault();
        show_reply_form($tweet.attr("tweet-id"));
    })
}

function setup_single_tweet() {
    let $tweet = $(this)
    let $media = $tweet.find(".tweet-media");
    $media.each(function () {
        rearrange_images($(this));
    })
    $media.each(setup_gif);

    // Convert each tweets emoji into twemojis
    $tweet.each(parse_twemoji);

    // Convert dates to time elapsed
    let dates = $tweet.find(".tweet-date");
    dates.each(fix_tweet_timestamp);

    // make like button clickable
    // NOTE: I'm using one() instead of click() to
    // prevent the user from sending multiple requests in
    // a very short time, the like_tweet_AJAX function will rebind
    // itself to the button once the request finishes
    $tweet.each(set_like_btns)

    // Make each poll choice clickable
    // NOTE: I'm using one() here for the same reason as above 
    let poll_btns = $tweet.find(".poll-choice-wrapper");
    poll_btns.one("click", choose_poll_option_AJAX);

    // Make each poll reflect whether or not the user has voted in it
    let polls = $tweet.find(".tweet-media-poll");
    polls.each(setup_poll_choice);

    // Convert end dates to time left
    let poll_dates = $tweet.find(".poll-time-left");
    poll_dates.each(fix_poll_timestamp);

    $tweet.each(set_comment_btns)
}

/**
 * Adds the 'chosen' and 'not-chosen' classes where necessary
 */
function setup_poll_choice() {
    let num = $(this).attr("user-choice");
    if (num != "None") {

        var $choices = $(this).find(".poll-choice-wrapper");

        var $chosen = $(this).find(`[choice-num="${num}"]`);

        $choices.addClass("not-chosen");
        $chosen.addClass("chosen");
        $chosen.removeClass("not-chosen");
    }
    $(this).each(calc_poll_perc);
}

/**
 * Updates the percentage values of the given poll
 */
function calc_poll_perc() {
    var $choice1 = $(this).find("[choice-num='1']");
    var $choice2 = $(this).find("[choice-num='2']");
    var $choice3 = $(this).find("[choice-num='3']");
    var $choice4 = $(this).find("[choice-num='4']");

    var total_votes = $(this).find(".poll-totalvotes .num").text();

    let choices = [$choice1, $choice2, $choice3, $choice4];
    for (let i = 0; i < 4; i++) {
        $ch = choices[i]
        if ($ch) {
            if (total_votes > 0) {
                var perc = Math.round($ch.attr("votes") / total_votes * 100);
                $ch.find(".poll-choice-perc").text(perc + "%");
            } else {
                var perc = 100;
                $ch.find(".poll-choice-perc").text("");
            }
            $ch.find(".poll-choice-bar").css("width", perc + "%");
        }
    }

}

/**
 * Updates the poll by adding/removing the amount of votes.
 * Note: This also calls calc_poll_perc on the given poll.
 * @param {Jquery selector} $poll 
 * @param {Number} prev the choice-num of the previous selection
 * @param {Number} updated the choice-num of the new selection
 */
function change_users_vote($poll, prev, updated) {
    var $total_votes = $poll.find(".poll-totalvotes .num");
    var $all_choices = $poll.find("[choice-num]");

    if (prev && prev != "None") {
        // reduce the number of votes by 1
        let $prev_vote = $poll.find(`[choice-num="${prev}"`);
        $prev_vote.attr("votes", -1 + +$prev_vote.attr("votes"));
        $total_votes.text(-1 + +$total_votes.text());

        // reset the poll to its 'unvoted' state
        $poll.attr("user-choice", "None");
        $all_choices.removeClass("not-chosen");
        $all_choices.removeClass("chosen");
    }

    if (updated && updated != "None") {
        // increase the number of votes by 1
        let $new_vote = $poll.find(`[choice-num="${updated}"]`);
        $new_vote.attr("votes", 1 + +$new_vote.attr("votes"));
        $total_votes.text(1 + +$total_votes.text());

        // reset the poll to its 'unvoted' state
        $all_choices.addClass("not-chosen");
        $all_choices.removeClass("chosen");

        // mark the update choice as selected        
        $poll.attr("user-choice", updated);
        $new_vote.addClass("chosen");
        $new_vote.removeClass("not-chosen");
    }

    $poll.each(calc_poll_perc);

}

/**
 * Sends an AJAX POST request that adds/removes the PollVote based on
 * this elements "chosen" class
 */
function choose_poll_option_AJAX() {
    var $btn = $(this);
    var $poll = $(this).closest(".tweet-media-poll");
    var tweet_id = $(this).closest(".tweet-container").attr("tweet-id");

    if ($(this).hasClass("chosen"))
        var num = null;
    else
        var num = $(this).attr("choice-num");

    var voted_before = $poll.attr("user-choice");

    $.ajax({
        url: "/ajax/choose_poll_option/",
        data: {
            "tweet_id": tweet_id,
            "choice": num
        },
        type: "post",
        dataType: "json",
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        success: function (response) {
            change_users_vote($poll, voted_before, response.voted);
            $btn.one("click", choose_poll_option_AJAX);
        }
    });
}

function get_single_tweet_AJAX(tweet_id, minified, callback) {
    $.ajax({
        url: "/ajax/get_single_tweet/",
        data: {
            "tweet_id": tweet_id,
            "minified": minified
        },
        type: "get",
        dataType: "html",
        success: function (response) {
            $tweet = $($.parseHTML(response)).find(".tweet-container");
            callback($tweet)
        }
    });
}

/**
 * Sends an AJAX GET request and appends the tweet list with received elements
 */
function get_tweet_list_AJAX(callback) {
    $.ajax({
        url: "/ajax/get_tweets/",
        dataType: "html",
        type: "get",
        success: function (response) {
            new_tweet_list = $($.parseHTML(response)).find(".tweet-container");
            callback(new_tweet_list)
        }
    });
}

function load_single_tweet(tweet_id, callback, minified = false) {
    get_single_tweet_AJAX(
        tweet_id,
        minified,
        function ($tweet) {
            $tweet.each(setup_single_tweet)
            callback($tweet)
        })
}

function load_tweet_list(callback) {
    get_tweet_list_AJAX(function ($list) {
        setup_tweet_list($list);
        var $tweet_date = $list.find(".tweet-date")
        var $poll_time_left = $list.find(".poll-time-left")

        // Change all dates from UNIX timestamps to user-readable timestamps
        $tweet_date.each(fix_tweet_timestamp);
        $poll_time_left.each(fix_poll_timestamp);

        // update the timestamps every couple seconds
        setInterval(function () {
            $tweet_date.each(fix_tweet_timestamp);
            $poll_time_left.each(fix_poll_timestamp);
        }, 5000);

        callback($list)
    })
}
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

    $btn.one("click", function (e) {
        e.stopPropagation();

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
            $btn.one("click", function (e) {
                e.stopPropagation();
                like_tweet_AJAX($tweet, $btn, $counter);
            })
        }
    });
}


function set_rt_btns() {
    let $tweet = $(this).closest(".tweet-container");
    let $rt_btn = $tweet.find(".rt-btn");
    let $dropdown = $tweet.find(".rt-dropdown");
    let $counter = $tweet.find(".tweet-rts-num");
    let tweet_id = $tweet.attr("tweet-id");

    $rt_btn.click(function (e) {
        e.stopPropagation();
        $dropdown.toggle();
    })

    $tweet.find(".rt-no-comment").click(function (e) {
        e.stopPropagation();
        rt_tweet_AJAX(tweet_id, $rt_btn, $counter);
    })

    $tweet.find(".rt-with-comment").click(function (e) {
        e.stopPropagation();
        // simulate a click to hide the dropdown
        $rt_btn.trigger("click");
        show_retweet_form(tweet_id, true);
    })
}


function set_link_btns() {
    let $tweet = $(this).closest(".tweet-container");
    let $link_btn = $tweet.find(".link-btn");
    let tweet_id = $tweet.attr("tweet-id");
    let author_id = $tweet.attr("author-username");
    let $dropdown = $tweet.find(".link-dropdown");
    let $copy_link = $tweet.find(".copy-link");

    $link_btn.click(function (e) {
        e.stopPropagation();
        $dropdown.toggle();
    })

    if ($copy_link[0])
        var clipboard = new ClipboardJS($copy_link[0], {
            text: function () {
                let base = window.location.origin
                let url = `${base}/${author_id}/status/${tweet_id}`
                return url
            }
        });

    $(this).find(".copy-link").click(function (e) {
        e.stopPropagation();
        $dropdown.toggle();

    })

}


function rt_tweet_AJAX(tweet_id, $btn, $counter) {
    var num_rts = $counter.text();
    $.ajax({
        url: "/ajax/rt/",
        data: {
            "tweet_id": tweet_id,
        },
        type: "post",
        dataType: "json",
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        success: function (response) {
            $btn.addClass("is-rt");
            $counter.text(1 + +num_rts);
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
    $tweets.each(make_bg_clickable)
}

function make_bg_clickable() {
    $(this).one("click", function (e) {
        e.stopPropagation();
        let id = $(this).find(".tweet-container").attr("tweet-id");
        let author = $(this).find(".tweet-container").attr("author-username");
        show_single_tweet(id, author, push_state = true);
    })
}



function set_comment_btns() {
    var $tweet = $(this).closest(".tweet-container");
    var $btn = $tweet.find(".comment-btn");
    var $counter = $tweet.find(".tweet-comments-num");

    $btn.click(function (e) {
        e.stopPropagation();
        show_reply_form($tweet.attr("tweet-id"));
    })
}

function setup_single_tweet() {
    let $tweet = $(this).find(".tweet-container");
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

    // Make the reply form appear when the comment btn is pressed
    $tweet.each(set_comment_btns);

    // Make the rt button clickable
    $tweet.each(set_rt_btns);

    // Make the link button clickable
    $tweet.each(set_link_btns);

    let nested_tweet = $tweet.find(".nested-tweet");
    nested_tweet.each(make_bg_clickable);

    // Make the @ clickable
    let clickable_name = $tweet.find('.tweet-clickable-name');
    clickable_name.click(function (e) {
        e.stopPropagation();
        let profile_id = $(this).closest(".tweet-container").attr("author-username");
        show_profile(profile_id, true);
    })

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
            let $response = $($.parseHTML(response));
            $tweet = $response.closest("#single-tweet");
            $comments = $response.closest("#comment-list");
            callback($tweet, $comments);
        }
    });
}

/**
 * Sends an AJAX GET request and appends the tweet list with received elements
 */
function get_tweet_list_AJAX(single_author, callback) {
    $.ajax({
        url: "/ajax/get_tweets/",
        data: {
            single_author: single_author
        },
        dataType: "html",
        type: "get",
        success: function (response) {
            new_tweet_list = $($.parseHTML(response)).find(".tweet-in-list");
            callback(new_tweet_list)
        }
    });
}


function load_single_tweet(tweet_id, callback, minified = false) {
    get_single_tweet_AJAX(
        tweet_id,
        minified,
        function ($tweet, $comments) {
            $tweet.each(setup_single_tweet);
            $comments.each(setup_single_tweet);
            callback($tweet, $comments);
        })
}


function load_tweet_list(callback, single_author = null) {
    get_tweet_list_AJAX(
        single_author,
        function ($list) {
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
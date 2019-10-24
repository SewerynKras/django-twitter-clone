function load_profile(profile_id, callback, push_state = false) {
    get_profile_AJAX(profile_id,
        function ($profile) {
            var $counter = $profile.find("#profile-followers .num");
            $profile.find("#follow-btn").one("click", function () {
                follow_AJAX(profile_id, $(this), $counter)
            })
            callback($profile)
        })
}

function follow_AJAX(profile_id, $btn, $counter) {
    var num_follows = $counter.text();
    $.ajax({
        url: "/ajax/follow/",
        data: {
            "profile_id": profile_id
        },
        type: "post",
        dataType: "json",
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        success: function (response) {
            if (response.followed == true) {
                num_follows = 1 + +num_follows;
                $btn.addClass("is-followed");
                $btn.text("Following");
            } else {
                num_follows = -1 + +num_follows;
                $btn.removeClass("is-followed");
                $btn.text("Follow");
            }
            $counter.text(num_follows);
            $btn.one("click", function (e) {
                e.stopPropagation();
                follow_AJAX(profile_id, $btn, $counter);
            })
        }
    });
}


function get_profile_AJAX(profile_id, callback) {
    $.ajax({
        url: "/ajax/get_profile/",
        data: {
            profile_id: profile_id
        },
        type: "get",
        dataType: "html",
        success: function (response) {
            var profile = $($.parseHTML(response));
            callback(profile);
        },
        error: function (request, status, error) {
            console.log({
                request,
                status,
                error
            });
        }
    });
}
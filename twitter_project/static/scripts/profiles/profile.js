function load_profile(profile_id, callback) {
    get_profile_AJAX(profile_id,
        function ($profile) {
            var $counter = $profile.find("#profile-followers .num");
            var $btn = $profile.find("#follow-btn");
            var follow_fnc = function (response) {

                var num_follows = $counter.text();

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
                    follow_AJAX(profile_id, follow_fnc);
                })
            }
            // Re-assign the AJAX call to the button recursively
            // after the initial call finishes
            $btn.one("click", function (e) {
                e.stopPropagation();
                follow_AJAX(profile_id, follow_fnc);
            })
            callback($profile);
        })
}

function follow_AJAX(profile_id, callback = null) {
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
            if (callback)
                callback(response);
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
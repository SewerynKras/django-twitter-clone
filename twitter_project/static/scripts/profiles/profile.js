function load_profile(profile_id, callback, push_state = false) {
    get_profile_AJAX(profile_id,
        function ($profile) {
            callback($profile)
        })
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
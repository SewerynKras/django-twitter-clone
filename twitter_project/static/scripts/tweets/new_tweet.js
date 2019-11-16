const HTML_X = "&times;";
const HTML_ARROW = "&larr;";
const AJAX_GIF_LIMIT = 12;


function load_new_tweet_AJAX(retweet_to = "", callback) {
    $.ajax({
        url: "/ajax/get_new_tweet_form/",
        type: "get",
        data: {
            retweet_to: retweet_to
        },
        dataType: "html",
        success: function (response) {
            $form = $($.parseHTML(response));
            callback($form);
        },
    });
}


$(document).ready(function () {
    var GIF_SEARCHED = false;

    var $gif_search_bar = $gif_selector.find("#gif-search-bar");
    var $gif_list = $gif_selector.find("#gif-list");
    var $gif_prev_list = $gif_selector.find("#gif-preview-list");
    var $gif_icon_btn = $gif_selector.find("#gif-icon-btn");
    var $gif_icon_btn_text = $gif_selector.find("#gif-icon-btn-text");

    $gif_icon_btn.click(function (e) {
        e.preventDefault();
        hide_gif_selector();
    })
    $gif_selector.find("#gif-search-submit").click(function (e) {
        e.preventDefault();
        search_gifs();
    })

    $gif_prev_list.find(".gif-preview").each(set_gif_thumb);

    $gif_prev_list.find(".gif-preview").click(function (e) {
        e.preventDefault();
        select_gif_prev_list($(this));
    })


    /**
     * Hides the gif selector.
     */
    function hide_gif_selector(force) {
        if (GIF_SEARCHED && !force) {
            $gif_icon_btn_text.html(HTML_X);
            reset_gif_list();
        } else {
            $cover.hide();
            $gif_selector.hide();
        }
    }

    /**
     * Calls query_gifs on the 
     */
    function search_gifs() {
        let query = $gif_search_bar.val();
        if (query != "") {
            $gif_icon_btn_text.html(HTML_ARROW);
            $gif_prev_list.hide();
            $gif_list.show();
            GIF_SEARCHED = true;
            query_gifs(query, 0);
        }
    }

    /**
     * Sends an AJAX request to the giphy api and appends
     * received gifs to the gif list
     * @param {String} query 
     * @param {Number} offset
     */
    function query_gifs(query, offset) {
        $gif_list.empty();
        $.ajax({
            url: "/ajax/get_gifs/",
            data: {
                "query": query,
                "limit": AJAX_GIF_LIMIT,
                "offset": offset
            },
            dataType: "html",
            success: function (response) {
                new_gif_list = $($.parseHTML(response));
                new_gif_list.each(set_gif_url);
                new_gif_list.click(select_gif);
                $gif_list.append(new_gif_list);
            },
        });
    }

    /**
     * Changes the search bars text to that of the given gif-preview
     * @param {Jquery selector} $preview 
     */
    function select_gif_prev_list($preview) {
        $gif_search_bar.val($.trim($preview.find(".gif-preview-text").text()));
    }

    /**
     * Resets the gif-list to its original state
     */
    function reset_gif_list() {
        $gif_list.empty();
        $gif_list.hide();
        $gif_prev_list.show();
        GIF_SEARCHED = false;
        $gif_search_bar.val("");
    }
    /**
     * Slots the selected gif to the gif media field,
     * hides and resets the gif selector.
     */
    function select_gif() {
        reset_gif_list();
        hide_gif_selector();
        event = new CustomEvent("gif-selected", {
            detail: {
                gif_url: $(this).attr("gif-url"),
                thumb_url: $(this).attr("thumb-url")
            }
        });
        window.dispatchEvent(event);
    }

    reset_gif_list()
});

function load_new_tweet_form(callback, replying_to = "", retweet_to = "") {
    load_new_tweet_AJAX(
        retweet_to,
        function ($form) {

            var $barLeft = $form.find(".new-tweet-bar-l");
            var $barRight = $form.find(".new-tweet-bar-r");
            var $textfield = $form.find(".new-tweet-textarea");
            var $placeholder = $form.find(".new-tweet-placeholder");

            var $media = $form.find(".tweet-media");

            var $img_media_button = $form.find(".new-tweet-media-image");
            var $gif_media_button = $form.find(".new-tweet-media-gif");
            var $poll_media_button = $form.find(".new-tweet-media-poll");
            var $emoji_media_button = $form.find(".new-tweet-media-emoji");

            var $image_button = $form.find(".new-tweet-image-button");
            var $images_media = $media.find(".tweet-media-images");
            var $image1_cont = $images_media.find("[image-num='1']");
            var $image2_cont = $images_media.find("[image-num='2']");
            var $image3_cont = $images_media.find("[image-num='3']");
            var $image4_cont = $images_media.find("[image-num='4']");
            var $image1 = $image1_cont.find(".tweet-image");
            var $image2 = $image2_cont.find(".tweet-image");
            var $image3 = $image3_cont.find(".tweet-image");
            var $image4 = $image4_cont.find(".tweet-image");
            var $gif_media = $media.find(".tweet-media-gif");
            var $gif_img = $gif_media.find("img");

            var $poll_media = $form.find(".tweet-media-poll");
            var $poll_exit_btn = $poll_media.find(".exit-btn");
            var $poll_ch1 = $poll_media.find("[choice-num='1']");
            var $poll_ch2 = $poll_media.find("[choice-num='2']");
            var $poll_ch3 = $poll_media.find("[choice-num='3']");
            var $poll_ch4 = $poll_media.find("[choice-num='4']");
            var $poll_ch2_btn = $poll_ch2.find("[type='button']");
            var $poll_ch3_btn = $poll_ch3.find("[type='button']");

            var $poll_date_days = $poll_media.find("select[name='days']");
            var $poll_date_hours = $poll_media.find("select[name='hours']");
            var $poll_date_minutes = $poll_media.find("select[name='minutes']");

            var $submit_btn = $form.find(".new-tweet-submit");

            /**
             * Returns the textfields text with emojis and whitespace.
             */
            function get_raw_text() {
                let raw = $textfield.clone();
                raw.find("img").each(function () {
                    $(this).html($(this).attr("alt"))
                })
                return raw.text();
            }

            /**
             * - removes the placeholder if the textfield isn't empty
             * - updates the progress bar
             * - converts standard emojis to their twemoji counterparts
             */
            function check_tweet_len() {
                let text_len = get_raw_text().length;
                if (text_len > 0) {
                    $placeholder.text("");
                    $textfield.addClass("expanded");
                    $submit_btn.removeClass("disabled");
                } else {
                    $placeholder.text($placeholder.attr("placeholder"));
                    $textfield.removeClass("expanded");
                    $submit_btn.addClass("disabled");
                }
                updateBar(Math.floor(text_len * 100 / 256));
                twemoji.parse($textfield[0]);
            }

            /**
             * Updates the progress bar based on the given value
             * @param {int} val Percentage value
             */
            function updateBar(val) {
                if (val <= 50) {
                    var deg = val / 100 * 360;
                    $barRight.css('transform', 'rotate(' + deg + 'deg)');
                    $barLeft.css('transform', 'rotate(0deg)');
                } else {
                    $barRight.css('transform', 'rotate(180deg)');
                    var deg = (val - 50) / 100 * 360;
                    $barLeft.css('transform', 'rotate(' + deg + 'deg)');
                }
            }

            /**
             * Resets and hides all media elements, enables media buttons.
             */
            function hide_all_media() {
                $media.hide();
                $images_media.hide();
                $gif_media.hide();
                $poll_media.hide();

                $img_media_button.prop('disabled', false);
                $gif_media_button.prop('disabled', false);
                $poll_media_button.prop('disabled', false);
            }
            /**
             * Hides all media,
             * Disables the img and poll buttons,
             * Shows gif media.
             */
            function show_gif_media() {
                hide_all_media();
                $img_media_button.prop('disabled', true);
                $poll_media_button.prop('disabled', true);

                $media.show();
                $gif_media.show();
            }

            /**
             * Hides all media,
             * Disables the gif and poll buttons,
             * Shows img media.
             */
            function show_img_media() {
                hide_all_media();
                $gif_media_button.prop('disabled', true);
                $poll_media_button.prop('disabled', true);

                $media.show();
                $images_media.show();
            }

            /**
             * Hides all media,
             * Disables the img and gif buttons,
             * Shows poll media.
             */
            function show_poll_media() {
                hide_all_media();
                $gif_media_button.prop('disabled', true);
                $img_media_button.prop('disabled', true);

                $media.show();
                $poll_media.show();
            }

            /**
             * Slots each image from $image_button to a free image container
             */
            function order_images() {
                if (this.files && this.files[0]) {
                    show_img_media();
                    if (this.files[0])
                        slot_image(this.files[0]);
                    if (this.files[1])
                        slot_image(this.files[1]);
                    if (this.files[2])
                        slot_image(this.files[2]);
                    if (this.files[3])
                        slot_image(this.files[3]);
                }
            }

            /**
             * Finds the first empty image container and fills it with the given image file
             * @param {File} file Image file fed that will be fed to the FileReader
             */
            function slot_image(file) {
                var reader = new FileReader();

                reader.onload = function (e) {
                    // find the first empty img tag and fill it with the given image
                    if (!$image1.attr("src")) {
                        $image1.attr("src", e.target.result);
                        $image1_cont.show();
                    } else if (!$image2.attr("src")) {
                        $image2.attr("src", e.target.result);
                        $image2_cont.show();
                    } else if (!$image3.attr("src")) {
                        $image3.attr("src", e.target.result);
                        $image3_cont.show();
                    } else if (!$image4.attr("src")) {
                        $image4.attr("src", e.target.result);
                        $image4_cont.show();
                    }
                    rearrange_images($images_media);
                }
                reader.readAsDataURL(file);

            }

            /**
             * Frees-up the image container by removing the stored image.
             * This also cascades all images.
             */
            function delete_image() {
                var image = $(this).find(".tweet-image");
                image.removeAttr("src");
                $(this).hide();
                cascade_images();
            }

            /**
             * Cascades all submitted images down by changing their 'src' attributes
             * around and hiding/showing image containers.
             */
            function cascade_images() {
                if (!($image1.attr("src")) && ($image2.attr("src"))) {
                    $image1.attr("src", $image2.attr("src"))
                    $image1_cont.show();

                    $image2.removeAttr("src")
                    $image2_cont.hide();
                }
                if (!$image2.attr("src") && $image3.attr("src")) {
                    $image2.attr("src", $image3.attr("src"))
                    $image2_cont.show();

                    $image3.removeAttr("src")
                    $image3_cont.hide();
                }
                if (!$image3.attr("src") && $image4.attr("src")) {
                    $image3.attr("src", $image4.attr("src"))
                    $image3_cont.show();

                    $image4.removeAttr("src")
                    $image4_cont.hide();
                }
                if (!$image1.attr("src")) {
                    hide_all_media();
                }

                rearrange_images($images_media);
            }

            /**
             * Changes the gif media fields attributes to
             * reflect the selected gif.
             */
            window.addEventListener("gif-selected", function (e) {
                show_gif_media();
                detail = e.detail
                $gif_img.attr("gif-url", detail.gif_url);
                $gif_img.attr("thumb-url", detail.thumb_url);
                $gif_img.attr("src", detail.gif_url);
            })

            /**
             * Clears the gif media field.
             */
            function delete_gif() {
                $gif_img.attr("gif-url", "");
                $gif_img.attr("thumb-url", "");
                $gif_img.attr("src", "");
                hide_all_media();
            }

            /**
             * Sends an AJAX POST request to create a new tweet
             */
            function new_tweet_AJAX() {

                if ($image1.attr("src")) {
                    var type = 'img';
                    var values = {
                        "image_1": $image1.attr("src"),
                        "image_2": $image2.attr("src"),
                        "image_3": $image3.attr("src"),
                        "image_4": $image4.attr("src")
                    };
                } else if ($gif_img.attr("src")) {
                    var type = 'gif';
                    var values = {
                        'thumb_url': $gif_img.attr("thumb-url"),
                        'gif_url': $gif_img.attr("gif-url")
                    };
                } else if ($poll_ch1.find("input").val()) {
                    var type = 'poll';
                    var values = {
                        "choice1_text": $poll_ch1.find("input").val(),
                        "choice2_text": $poll_ch2.find("input").val(),
                        "choice3_text": $poll_ch3.find("input").val(),
                        "choice4_text": $poll_ch4.find("input").val(),
                        "days_left": $poll_date_days.val(),
                        "hours_left": $poll_date_hours.val(),
                        "minutes_left": $poll_date_minutes.val()
                    };
                } else {
                    var type = null;
                    var values = null;
                };
                if (type)
                    var media = {
                        type: type,
                        values: values
                    }
                else
                    var media = null

                let data = {
                    "text": get_raw_text(),
                    "replying_to": replying_to,
                    "retweet_id": retweet_to,
                    "media": media
                };
                $.ajax({
                    url: "/ajax/new_tweet/",
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken')
                    },
                    data: JSON.stringify(data),
                    type: "post",
                    dataType: "json",
                    success: function () {
                        $submit_btn.removeClass("disabled");
                        $submit_btn.one("click", new_tweet_AJAX)
                        $textfield.text("");
                        check_tweet_len();
                        $reply_form.hide();
                        hide_all_cover();
                        hide_all_media()
                        check_first_tweet();
                    },
                    error: function (response) {
                        console.log(response)
                        $submit_btn.removeClass("disabled");
                        $submit_btn.one("click", new_tweet_AJAX)
                        check_tweet_len();
                    }
                });

            }

            $placeholder.text($placeholder.attr("placeholder"));

            $placeholder.click(function () {
                $textfield.focus();
            })

            $textfield.on("keypress paste", function (e) {
                if (get_raw_text().length >= 256) {
                    e.preventDefault();
                    return false;
                }
            });
            $textfield.on('input', check_tweet_len);

            $submit_btn.one("click", function (e) {
                e.preventDefault();
                $(this).addClass("disabled");
                new_tweet_AJAX();
            })

            $emoji_media_button.lsxEmojiPicker({
                twemoji: true,
                height: 200,
                width: 240,
                onSelect: function (emoji) {
                    if (get_raw_text().length < 256) {
                        $textfield.append("<span>" + emoji.value + "<span>");
                        check_tweet_len();
                    }
                }
            });

            $img_media_button.click(function (e) {
                e.preventDefault();
                $image_button.click();
            })

            $image_button.change(order_images);

            $($image1_cont).click(delete_image);
            $($image2_cont).click(delete_image);
            $($image3_cont).click(delete_image);
            $($image4_cont).click(delete_image);

            $gif_media_button.click(function (e) {
                e.preventDefault();
                show_gif_selector();
            })

            $gif_img.click(delete_gif);

            $poll_media_button.click(function (e) {
                e.preventDefault();
                show_poll_media();
            })

            $poll_ch2_btn.click(function (e) {
                e.preventDefault();
                $(this).hide();
                $poll_ch3.show();
            })
            $poll_ch3_btn.click(function (e) {
                e.preventDefault();
                $(this).hide();
                $poll_ch4.show();
            })

            $poll_exit_btn.click(function (e) {
                e.preventDefault();
                hide_all_media();
            })

            callback($form);
        })
}
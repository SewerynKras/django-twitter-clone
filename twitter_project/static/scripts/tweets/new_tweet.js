const HTML_X = "&times;";
const HTML_ARROW = "&larr;";
const AJAX_GIF_LIMIT = 12;

var GIF_SEARCHED = false;


var $cover;

var $barLeft;
var $barRight;
var $placeholder;
var $textfield;

var $media;

var $img_media_button;
var $gif_media_button;
var $poll_media_button;
var $emoji_media_button;

var $image_button;
var $images_media;
var $image1;
var $image2;
var $image3;
var $image4;
var $image1_cont;
var $image2_cont;
var $image3_cont;
var $image4_cont;
var $gif_media;

var $poll_media;
var $poll_exit_btn;
var $poll_ch1;
var $poll_ch2;
var $poll_ch3;
var $poll_ch4;

var $poll_date_days;
var $poll_date_hours;
var $poll_date_minutes;

var $poll_ch2_btn;
var $poll_ch3_btn;

var $gif_prev_list;

var $gif_selector;
var $gif_search_bar;
var $gif_list;
var $gif_icon_btn;
var $gif_icon_btn_text;


/**
 * - removes the placeholder if the textfield isn't empty
 * - updates the progress bar
 * - converts standard emojis to their twemoji counterparts
 */
function check_tweet_len() {
    let text_len = $textfield.text().length;
    if (text_len > 0) {
        $placeholder.text("");
        $textfield.addClass("expanded");
    } else {
        $placeholder.text($placeholder.attr("placeholder"));
        $textfield.removeClass("expanded");
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

    $img_media_button.prop('disabled', false)
    $gif_media_button.prop('disabled', false)
    $poll_media_button.prop('disabled', false)
}
/**
 * Hides all media,
 * Disables the img and poll buttons,
 * Shows gif media.
 */
function show_gif_media() {
    hide_all_media();
    $img_media_button.prop('disabled', true)
    $poll_media_button.prop('disabled', true)

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
    $gif_media_button.prop('disabled', true)
    $poll_media_button.prop('disabled', true)

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
    $gif_media_button.prop('disabled', true)
    $img_media_button.prop('disabled', true)

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
    var image = $form.find(this).find(".tweet-image");
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
 * Displays the gif selector.
 */
function show_gif_selector() {
    $cover.show();
    $gif_selector.show();
}

/**
 * Hides the gif selector.
 */
function hide_gif_selector(force) {
    if (GIF_SEARCHED) {
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
            new_gif_list = $form.find($.parseHTML(response));
            new_gif_list.each(set_gif_url);
            new_gif_list.click(select_gif);
            $gif_list.append(new_gif_list);

        },
    });
}

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
    $gif_prev_list.show();
    GIF_SEARCHED = false;
    $gif_search_bar.val("");
}

/**
 * Changes the gif media fields attributes to
 * reflect the selected gif.
 * @param {Jquery selector} $gif 
 */
function slot_gif($gif) {
    show_gif_media();
    $gif_img.attr("gif-url", $gif.attr("gif-url"))
    $gif_img.attr("thumb-url", $gif.attr("thumb-url"))
    $gif_img.attr("src", $gif_img.attr("gif-url"));
}

/**
 * Slots the selected gif to the gif media field,
 * hides and resets the gif selector.
 */
function select_gif() {
    slot_gif($(this));
    reset_gif_list();
    hide_gif_selector();
}

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

    let data = {
        "text": $textfield.text(),
        "media": {
            "type": type,
            "values": values
        },
    };
    console.log(data);
    $.ajax({
        url: "/new_tweet/",
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        data: JSON.stringify(data),
        type: "post",
        dataType: "json",
        success: function (response) {
            console.log(response);
        },
    });

}

function load_new_tweet_AJAX(callback) {
    $.ajax({
        url: "/ajax/get_new_tweet_form/",
        type: "get",
        dataType: "html",
        success: function (response) {
            $form = $($.parseHTML(response))
            callback($form)
        },
    });
}

function load_new_tweet_form() {
    load_new_tweet_AJAX(function ($form) {

        // Fill jquery selectors
        $barLeft = $form.find(".new-tweet-bar-l");
        $barRight = $form.find(".new-tweet-bar-r");
        $textfield = $form.find(".new-tweet-textarea");
        $placeholder = $form.find(".new-tweet-placeholder");

        $cover = $form.find("#cover");
        $media = $form.find(".tweet-media");

        $img_media_button = $form.find(".new-tweet-media-image");
        $gif_media_button = $form.find(".new-tweet-media-gif");
        $poll_media_button = $form.find(".new-tweet-media-poll");
        $emoji_media_button = $form.find(".new-tweet-media-emoji");

        $image_button = $form.find(".new-tweet-image-button");
        $images_media = $media.find(".tweet-media-images");
        $image1_cont = $images_media.find("[image-num='1']");
        $image2_cont = $images_media.find("[image-num='2']");
        $image3_cont = $images_media.find("[image-num='3']");
        $image4_cont = $images_media.find("[image-num='4']");
        $image1 = $image1_cont.find(".tweet-image");
        $image2 = $image2_cont.find(".tweet-image");
        $image3 = $image3_cont.find(".tweet-image");
        $image4 = $image4_cont.find(".tweet-image");
        $gif_media = $media.find(".tweet-media-gif");
        $gif_img = $gif_media.find("img");

        $poll_media = $form.find(".tweet-media-poll");
        $poll_exit_btn = $poll_media.find(".exit-btn");
        $poll_ch1 = $poll_media.find("[choice-num='1']");
        $poll_ch2 = $poll_media.find("[choice-num='2']");
        $poll_ch3 = $poll_media.find("[choice-num='3']");
        $poll_ch4 = $poll_media.find("[choice-num='4']");
        $poll_ch2_btn = $poll_ch2.find("[type='button']");
        $poll_ch3_btn = $poll_ch3.find("[type='button']");

        $poll_date_days = $poll_media.find("select[name='days']");
        $poll_date_hours = $poll_media.find("select[name='hours']");
        $poll_date_minutes = $poll_media.find("select[name='minutes']");

        $gif_selector = $form.find("#gif-selector");
        $gif_search_bar = $form.find("#gif-search-bar");
        $gif_list = $form.find("#gif-list");
        $gif_prev_list = $form.find("#gif-preview-list");
        $gif_icon_btn = $form.find("#gif-icon-btn");
        $gif_icon_btn_text = $form.find("#gif-icon-btn-text");

        $main_body.html($form)

        $placeholder.text($placeholder.attr("placeholder"));

        $placeholder.click(function () {
            $textfield.focus();
        })

        $textfield.on('input', check_tweet_len);

        $form.find(".new-tweet-submit").click(function (e) {
            e.preventDefault();
            new_tweet_AJAX();
        })

        $emoji_media_button.lsxEmojiPicker({
            twemoji: true,
            height: 200,
            width: 240,
            onSelect: function (emoji) {
                $textfield.append("<span>" + emoji.value + "<span>");
                check_tweet_len();
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

        $cover.click(function (e) {
            e.preventDefault();
            hide_gif_selector();
        })
        $gif_icon_btn.click(function (e) {
            e.preventDefault();
            hide_gif_selector();
        })

        $form.find("#gif-search-submit").click(function (e) {
            e.preventDefault();
            search_gifs();
        })

        $form.find(".gif-preview").each(set_gif_thumb);

        $form.find(".gif-preview").click(function (e) {
            e.preventDefault();
            select_gif_prev_list($(this));
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
    })
}
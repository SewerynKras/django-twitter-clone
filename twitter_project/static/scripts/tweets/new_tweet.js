const HTML_X = "&times;";
const HTML_ARROW = "&larr;";
const AJAX_GIF_LIMIT = 12;

var $cover;

var $barLeft;
var $barRight;
var $placeholder;
var $textfield;

var $media

var $image_button;
var $image1;
var $image2;
var $image3;
var $image4;
var $image1_cont;
var $image2_cont;
var $image3_cont;
var $image4_cont;

var $gif_selector;
var $gif_search_bar;
var $gif_list
var $gif_icon_btn;
var $gif_icon_btn_text;

var $hidden_image1_form;
var $hidden_image2_form;
var $hidden_image3_form;
var $hidden_image4_form;
var $hidden_text_input_form;

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
 * Slots each image from $image_button to a free image container
 */
function order_images() {
    if (this.files && this.files[0]) {
        $media.show();
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
        rearrange_images($media);
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
    if (!$image1.attr("src"))
        $media.hide();

    rearrange_images($media);
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
function hide_gif_selector() {
    $cover.hide();
    $gif_selector.hide();
}

/**
 * Calls query_gifs on the 
 */
function search_gifs() {
    let query = $gif_search_bar.val();
    if (query != "")
        query_gifs(query, 0);
}
/**
 * Sends an AJAX request to the giphy api and appends
 * received gifs to the gif list
 * @param {String} query 
 * @param {Number} offset
 */
function query_gifs(query, offset) {
    $.ajax({
        url: "ajax/get_gifs/",
        data: {
            "query": query,
            "limit": AJAX_GIF_LIMIT,
            "offset": offset
        },
        dataType: "html",
        success: function (response) {
            new_gif_list = $($.parseHTML(response))
            $gif_list.html(new_gif_list.filter("#gif-list").children())
        },
    });
}
/**
 * Changes the background-image css property to the url in
 * the 'gif-thumb' attribute
 */
function set_gif_thumb() {
    $(this).css("background-image", `url(${$(this).attr("gif-thumb")})`)
}

/**
 * Changes the background-image css property to the url in
 * the 'gif-url' attribute
 */
function set_gif_url() {
    $(this).css("background-image", `url(${$(this).attr("gif-thumb")})`)
}

/**
 * Changes the search bars text to that of the given gif-preview
 * @param {Jquery selector} $preview 
 */
function select_preview($preview) {
    $gif_search_bar.val($.trim($preview.find(".gif-preview-text").text()));
}

/**
 * Takes care of all hidden forms.
 * This should be called just before submitting.
 */
function fill_hidden_forms() {
    $hidden_text_input_form.val($textfield.text());
    $hidden_image1_form.val($image1.attr("src"));
    $hidden_image2_form.val($image2.attr("src"));
    $hidden_image3_form.val($image3.attr("src"));
    $hidden_image4_form.val($image4.attr("src"));
}

function new_tweet_AJAX() {
    let data = {
        "text": $textfield.text(),
        "media": {
            "type": "img",
            "values": [
                $image1.attr("src"),
                $image2.attr("src"),
                $image3.attr("src"),
                $image4.attr("src")
            ]
        },
    }
    console.log(data)
    $.ajax({
        url: "ajax/new_tweet/",
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        data: data,
        type: "post",
        dataType: "json",
        success: function (response) {
            console.log(response);
        },
    });

}

$(document).ready(function () {

    // Fill jquery selectors
    $barLeft = $(".new-tweet-bar-l");
    $barRight = $(".new-tweet-bar-r");
    $textfield = $(".new-tweet-textarea");
    $placeholder = $(".new-tweet-placeholder");

    $cover = $("#cover");
    $media = $(".tweet-media");

    $image_button = $(".new-tweet-image-button");
    $image1_cont = $media.find("[image-num='1']");
    $image2_cont = $media.find("[image-num='2']");
    $image3_cont = $media.find("[image-num='3']");
    $image4_cont = $media.find("[image-num='4']");
    $image1 = $image1_cont.find(".tweet-image");
    $image2 = $image2_cont.find(".tweet-image");
    $image3 = $image3_cont.find(".tweet-image");
    $image4 = $image4_cont.find(".tweet-image");

    $gif_selector = $("#gif-selector");
    $gif_search_bar = $("#gif-search-bar");
    $gif_list = $("#gif-list");
    $gif_icon_btn = $("#gif-icon-btn");
    $gif_icon_btn_text = $("#gif-icon-btn-text");

    $placeholder.text($placeholder.attr("placeholder"));

    $placeholder.click(function () {
        $textfield.focus();
    })

    $textfield.on('input', check_tweet_len);

    $("form").submit(function () {
        fill_hidden_forms();
        return true;
    })

    $(".new-tweet-submit").click(function (e) {
        e.preventDefault();
        new_tweet_AJAX();
    })

    $('.new-tweet-media-emoji').lsxEmojiPicker({
        twemoji: true,
        height: 200,
        width: 240,
        onSelect: function (emoji) {
            $textfield.append("<span>" + emoji.value + "<span>");
            check_tweet_len();
        }
    });

    $(".new-tweet-media-image").click(function (e) {
        e.preventDefault();
        $image_button.click();
    })

    $image_button.change(order_images);

    $($image1_cont).click(delete_image);
    $($image2_cont).click(delete_image);
    $($image3_cont).click(delete_image);
    $($image4_cont).click(delete_image);

    $(".new-tweet-media-gif").click(function (e) {
        e.preventDefault();
        show_gif_selector();
    })

    $($cover, $gif_icon_btn).click(function (e) {
        e.preventDefault();
        hide_gif_selector();
    })

    $("#gif-search-submit").click(function (e) {
        e.preventDefault();
        search_gifs();
    })

    $(".gif-preview").each(set_gif_thumb)

    $(".gif-preview").click(function (e) {
        e.preventDefault();
        select_preview($(this));
    })
});
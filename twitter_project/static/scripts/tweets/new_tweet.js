$(document).ready(function () {

    // JQUERY variables
    var $barLeft = $(".new-tweet-bar-l");
    var $barRight = $(".new-tweet-bar-r");
    var $textfield = $(".new-tweet-textarea");
    var $placeholder = $(".new-tweet-placeholder");
    var $cover = $("#cover");

    var $images = $("#new-tweet-images");

    var $image1 = $("#new-tweet-image-1");
    var $image2 = $("#new-tweet-image-2");
    var $image3 = $("#new-tweet-image-3");
    var $image4 = $("#new-tweet-image-4");

    var $image1_cont = $("#new-tweet-image-cont-1");
    var $image2_cont = $("#new-tweet-image-cont-2");
    var $image3_cont = $("#new-tweet-image-cont-3");
    var $image4_cont = $("#new-tweet-image-cont-4");


    // ----------------- TEXT -----------------

    $placeholder.text($placeholder.attr("placeholder"));
    $placeholder.click(function () {
        $textfield.focus();
    })

    $textfield.on('input', check_tweet_len);

    function check_tweet_len() {
        var text_len = $textfield.text().length;
        if (text_len > 0) {
            $placeholder.text("");
            $textfield.css("width", "50%");
        } else {
            $placeholder.text($placeholder.attr("placeholder"));
            $textfield.css("width", "1%");
        }
        updateBar(Math.floor(text_len * 100 / 256));
        twemoji.parse($textfield[0]);
    }

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


    // ----------------- FORM  ----------------- 

    $("form").submit(function () {
        // take care of all the hidden input fields
        $("#new-tweet-text-form").val($textfield.text());
        $("#new-tweet-image1-form").val($image1.attr("src"));
        $("#new-tweet-image2-form").val($image2.attr("src"));
        $("#new-tweet-image3-form").val($image3.attr("src"));
        $("#new-tweet-image4-form").val($image4.attr("src"));
        return true;
    })


    // ----------------- EMOJI -----------------

    // attach the emoji picker to the corresponding button
    $('.new-tweet-media-emoji').lsxEmojiPicker({
        twemoji: true,
        height: 200,
        width: 240,
        onSelect: function (emoji) {
            $textfield.append("<span>" + emoji.value + "<span>");
            check_tweet_len();
        }
    });


    // ----------------- IMAGES ----------------- 

    $(".new-tweet-media-image").click(function (e) {
        e.preventDefault();
        $("#new-tweet-image-button").click();
    })

    $("#new-tweet-image-button").change(function () {
        if (this.files && this.files[0]) {
            $images.show();
            if (this.files[0])
                slot_image(this.files[0]);
            if (this.files[1])
                slot_image(this.files[1]);
            if (this.files[2])
                slot_image(this.files[2]);
            if (this.files[3])
                slot_image(this.files[3]);
        }
    });

    // FIND A FREE SPOT AND PUT THE UPLOADED IMAGE THERE
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
            rearrange_images($images);
        }
        reader.readAsDataURL(file);

    }

    // DELETE IMAGE ON CLICK
    $($image1_cont, $image2_cont, $image3_cont, $image4_cont).click(function () {
        var image = $(this).find(".tweet-image");
        image.removeAttr("src");
        $(this).hide();

        // Cascade all other images down

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

        // hide the images container if there are no images left
        if (!$image1.attr("src"))
            $images.hide();

        rearrange_images($images);
    })

    // ----------------- GIFS ----------------- 

    $(".new-tweet-media-gif").click(function (e) {
        e.preventDefault();
        $cover.show();
        $("#gif-container").show();
    })

    $cover.add($("#gif-search-close-btn")).click(function (e) {
        e.preventDefault();
        $cover.hide();
        $("#gif-container").hide();
    })

    $("#gif-search-close-btn").click(function (e) {
        e.preventDefault();
    })

    $("#gif-search-submit").click(function (e) {
        e.preventDefault();
        let query = $("#gif-search-bar").val();
        if (query != "")
            query_gifs(query, 0);
    })

    $(".gif-preview").click(function (e) {
        e.preventDefault();
        // change the searchbar value to the selected gif preview
        $("#gif-search-bar").val($.trim($(this).find(".gif-preview-text").text()));
    })
});


// AJAX variables
var LIMIT = 12;


// ----------------- AJAX functions ----------------- 

function query_gifs(query, offset) {
    $.ajax({
        url: "ajax/get_gifs/",
        data: {
            "query": query,
            "limit": LIMIT,
            "offset": offset
        },
        dataType: "html",
        success: function (response) {
            gif_list = $($.parseHTML(response))
            $("#gif-preview-list").html(gif_list.filter("#gif-list"))
        },
    });
}
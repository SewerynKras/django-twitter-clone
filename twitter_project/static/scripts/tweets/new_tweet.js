$(document).ready(function () {
    var $barLeft = $(".new-tweet-bar-l")
    var $barRight = $(".new-tweet-bar-r")
    var $textfield = $(".new-tweet-textarea")
    var $placeholder = $(".new-tweet-placeholder")

    var $images = $(".new-tweet-images")

    var $image1 = $("#new-tweet-image-1")
    var $image2 = $("#new-tweet-image-2")
    var $image3 = $("#new-tweet-image-3")
    var $image4 = $("#new-tweet-image-4")

    var $image_cont_left = $(".new-tweet-image-cont-left")
    var $image_cont_right = $(".new-tweet-image-cont-right")

    var $image1_cont = $("#new-tweet-image-cont-1")
    var $image2_cont = $("#new-tweet-image-cont-2")
    var $image3_cont = $("#new-tweet-image-cont-3")
    var $image4_cont = $("#new-tweet-image-cont-4")

    $placeholder.text($placeholder.attr("placeholder"))
    $placeholder.click(function () {
        $textfield.focus()
    })
    $textfield.on('input', check_tweet_len)

    function updateBar(val) {
        if (val <= 50) {
            var deg = val / 100 * 360
            $barRight.css('transform', 'rotate(' + deg + 'deg)')
            $barLeft.css('transform', 'rotate(0deg)')
        } else {
            $barRight.css('transform', 'rotate(180deg)')
            var deg = (val - 50) / 100 * 360
            $barLeft.css('transform', 'rotate(' + deg + 'deg)')
        }
    }

    $("form").submit(function () {
        // take care of all the hidden input fields
        $("#new-tweet-text-form").val($textfield.text())
        return true
    })

    // attach the emoji picker to the corresponding button
    $('.new-tweet-media-emoji').lsxEmojiPicker({
        twemoji: true,
        height: 200,
        width: 240,
        onSelect: function (emoji) {
            $textfield.append("<span>" + emoji.value + "<span>")
            check_tweet_len()
        }
    });

    function check_tweet_len() {
        var text_len = $textfield.text().length
        if (text_len > 0) {
            $placeholder.text("")
            $textfield.css("width", "50%")
        } else {
            $placeholder.text($placeholder.attr("placeholder"))
            $textfield.css("width", "1%")
        }
        updateBar(Math.floor(text_len * 100 / 256))
        twemoji.parse($textfield[0])
    }

    $("#new-tweet-image-button").change(function () {
        if (this.files && this.files[0]) {
            $images.show()
            if (this.files[0])
                slot_image(this.files[0])
            if (this.files[1])
                slot_image(this.files[1])
            if (this.files[2])
                slot_image(this.files[2])
            if (this.files[3])
                slot_image(this.files[3])
        }
    });

    $(".new-tweet-media-image").click(function (e) {
        e.preventDefault();
        $("#new-tweet-image-button").click()
    })

    function slot_image(file) {
        var reader = new FileReader();

        reader.onload = function (e) {
            // find the first empty img tag and fill it with the given image
            if (!$image1.attr("src")) {
                $image1.attr("src", e.target.result);
                $image1_cont.removeAttr("hidden");
            } else if (!$image2.attr("src")) {
                $image2.attr("src", e.target.result);
                $image2_cont.removeAttr("hidden");
            } else if (!$image3.attr("src")) {
                $image3.attr("src", e.target.result);
                $image3_cont.removeAttr("hidden");
            } else if (!$image4.attr("src")) {
                $image4.attr("src", e.target.result);
                $image4_cont.removeAttr("hidden");
            }
            rearrange_images()
        }
        reader.readAsDataURL(file)

    }
    $(".new-tweet-image-cont").click(function () {
        var image = $(this).find(".new-tweet-image")
        image.removeAttr("src")
        $(this).attr("hidden", "true")

        // Cascade all other images down

        if (!($image1.attr("src")) && ($image2.attr("src"))) {
            $image1.attr("src", $image2.attr("src"))
            $image1_cont.removeAttr("hidden")

            $image2.removeAttr("src")
            $image2_cont.attr("hidden", "true")
        }
        if (!$image2.attr("src") && $image3.attr("src")) {
            $image2.attr("src", $image3.attr("src"))
            $image2_cont.removeAttr("hidden")

            $image3.removeAttr("src")
            $image3_cont.attr("hidden", "true")
        }
        if (!$image3.attr("src") && $image4.attr("src")) {
            $image3.attr("src", $image4.attr("src"))
            $image3_cont.removeAttr("hidden")

            $image4.removeAttr("src")
            $image4_cont.attr("hidden", "true")
        }

        // hide the images container if there are no images left
        if (!$image1.attr("src"))
            $images.hide()

        rearrange_images()
    })

    function rearrange_images() {
        // images should be cascaded down before
        // calling this function

        // by default all images will have
        // 50% height and width like so:

        // ------------------
        // |       |        |
        // |   1   |   2    |
        // |       |        |
        // --------|---------
        // |       |        |
        // |   3   |   4    |
        // |       |        |
        // ------------------
        $image1_cont.removeClass("tall")
        $image2_cont.removeClass("tall")
        $image3_cont.removeClass("tall")
        $image4_cont.removeClass("tall")

        $image_cont_left.removeClass("wide")
        $image_cont_right.removeClass("narrow")

        // if there is no fourth image the second one
        // should have its height changed to 100% like so:
        // ------------------
        // |       |        |
        // |   1   |        |
        // |       |        |
        // --------|   2    |
        // |       |        |
        // |   3   |        |
        // |       |        |
        // ------------------
        if (!$image4.attr("src"))
            $image2_cont.addClass("tall")

        // if there is no third image the first one
        // should have its height changed to 100% like so:
        // ------------------
        // |       |        |
        // |       |        |
        // |       |        |
        // |   1   |   2    |
        // |       |        |
        // |       |        |
        // |       |        |
        // ------------------
        if (!$image3.attr("src"))
            $image1_cont.addClass("tall")

        // if there is no second image the first one
        // should have its width changed to 100% like so:
        // ------------------
        // |                |
        // |                |
        // |                |
        // |       1        |
        // |                |
        // |                |
        // |                |
        // ------------------
        if (!$image2.attr("src")) {
            $image_cont_left.addClass("wide")
            $image1_cont.addClass("tall")
        }

    }
});
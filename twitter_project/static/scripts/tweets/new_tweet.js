$(document).ready(function () {
    var $barLeft = $(".new-tweet-bar-l")
    var $barRight = $(".new-tweet-bar-r")
    var $textfield = $(".new-tweet-textarea")
    var $placeholder = $(".new-tweet-placeholder")

    var $image1 = $("#new-tweet-image-1")
    var $image2 = $("#new-tweet-image-2")
    var $image3 = $("#new-tweet-image-3")
    var $image4 = $("#new-tweet-image-4")

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
        if (this.files) {
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

    $(".new-tweet-media-image").click(function () {
        $("#new-tweet-image-button").click()
    })

    function slot_image(file) {
        var reader = new FileReader();

        reader.onload = function (e) {
            // find the first empty img tag and fill it with the given image
            if (!$image1.attr("src")) {
                $image1.attr("src", e.target.result);
                $image1_cont.removeClass("new-tweet-image-hidden");
            } else if (!$image2.attr("src")) {
                $image2.attr("src", e.target.result);
                $image2_cont.removeClass("new-tweet-image-hidden");
            } else if (!$image3.attr("src")) {
                $image3.attr("src", e.target.result);
                $image3_cont.removeClass("new-tweet-image-hidden");
            } else if (!$image4.attr("src")) {
                $image4.attr("src", e.target.result);
                $image4_cont.removeClass("new-tweet-image-hidden");
            }
        }
        reader.readAsDataURL(file)
    }
    $(".new-tweet-image-cont").click(function () {
        var image = $(this).find(".new-tweet-image")
        image.removeAttr("src")
        $(this).addClass("new-tweet-image-hidden")

        // Cascade all other images down

        if (!($image1.attr("src")) && ($image2.attr("src"))) {
            $image1.attr("src", $image2.attr("src"))
            $image1_cont.removeClass("new-tweet-image-hidden")

            $image2.removeAttr("src")
            $image2_cont.addClass("new-tweet-image-hidden")
        }
        if (!$image2.attr("src") && $image3.attr("src")) {
            $image2.attr("src", $image3.attr("src"))
            $image2_cont.removeClass("new-tweet-image-hidden")

            $image3.removeAttr("src")
            $image3_cont.addClass("new-tweet-image-hidden")
        }
        if (!$image3.attr("src") && $image4.attr("src")) {
            $image3.attr("src", $image4.attr("src"))
            $image3_cont.removeClass("new-tweet-image-hidden")

            $image4.removeAttr("src")
            $image4_cont.addClass("new-tweet-image-hidden")
        }
    })

});
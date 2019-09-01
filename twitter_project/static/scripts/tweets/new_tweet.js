$(document).ready(function () {
    var $barLeft = $(".new-tweet-bar-l")
    var $barRight = $(".new-tweet-bar-r")
    var $textfield = $(".new-tweet-textarea")
    var $placeholder = $(".new-tweet-placeholder")

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
});
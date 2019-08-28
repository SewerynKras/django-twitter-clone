$(document).ready(function () {
    var $barLeft = $("#new-tweet-bar-l")
    var $barRight = $("#new-tweet-bar-r")
    var $textfield = $("#new-tweet-textarea")
    var $placeholder = $("#new-tweet-placeholder")

    $placeholder.text($placeholder.attr("placeholder"))
    $placeholder.click(function () {
        $textfield.focus()
    })
    $textfield.on('input', function () {
        var text_len = $(this).text().length
        if (text_len > 0)
            $placeholder.text("")
        else
            $placeholder.text($placeholder.attr("placeholder"))
        updateBar(Math.floor(text_len * 100 / 256))
    })

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
});
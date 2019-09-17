/**
 * Rearranges all images inside the given container so the overall
 * height and width doesn't change.
 * @param {Jquery selector} $images 
 */
function rearrange_images($images) {
    // images should be cascaded down before
    // calling this function

    // find the left and right container
    var $image_cont_left = $images.find(".tweet-image-cont-left");
    var $image_cont_right = $images.find(".tweet-image-cont-right");

    // find all image containers
    var $image1_cont = $image_cont_left.find("[image-num='1']");
    var $image3_cont = $image_cont_left.find("[image-num='3']");
    var $image2_cont = $image_cont_right.find("[image-num='2']");
    var $image4_cont = $image_cont_right.find("[image-num='4']");

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
    $image1_cont.removeClass("tall");
    $image2_cont.removeClass("tall");
    $image3_cont.removeClass("tall");
    $image4_cont.removeClass("tall");

    $image_cont_left.removeClass("wide");
    $image_cont_left.show();
    $image_cont_right.removeClass("narrow");
    $image_cont_right.show();
    $images.show();

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
    if (!$image4_cont.is(":visible"))
        $image2_cont.addClass("tall");

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
    if (!$image3_cont.is(":visible"))
        $image1_cont.addClass("tall");

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
    if (!$image2_cont.is(":visible")) {
        $image_cont_left.addClass("wide");
        $image_cont_right.addClass("narrow");
        $image1_cont.addClass("tall");
    }

    // hide the media element if there are no images
    if (!$image1_cont.is(":visible"))
        $images.hide();
}
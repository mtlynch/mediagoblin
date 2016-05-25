$(document).ready(function() {
    $(".lightbox").click(function() {
        overlayLink = $(this).attr("href");  //Getting the link for the media
        window.startOverlay(overlayLink);
        return false;
    });
});

function startOverlay(overlayLink) {

    // Adding elements to the page
    $("body")
        .append('<div class="overlay"></div><div class="box"></div>')
        .css({
            "overflow-y": "hidden"
        });

    // To create the lightbox effect
    $(".container").animate({
        "opacity": "0.2"
    }, 300, "linear");

    var imgWidth = $(".box img").width();
    var imgHeight = $(".box img").height();

    //adding the image to the box

    $(".box").html('<img height=100% width=100% src="' + overlayLink + '" alt="" />');
    //Position
    $(".box img").load(function() {
        var imgWidth = $(".box img").width();
        var imgHeight = $(".box img").height();
        if (imgHeight > screen.height - 170) imgHeight = screen.height - 170;
        if (imgWidth > screen.width - 300) imgWidth = screen.width - 300;
        $(".box")
            .css({
                "position": "absolute",
                "top": "50%",
                "left": "50%",
                "height": imgHeight + 10,
                "width": imgWidth + 10,
                "border": "5px solid white",
                "margin-top": -(imgHeight / 2),
                "margin-left": -(imgWidth / 2) //to position it in the middle
            })
            .animate({
                "opacity": "1"
            }, 400, "linear");

        //To remove
        window.closeOverlay();
    });
}

function closeOverlay() {
    // allow users to be able to close the lightbox
    $(".overlay").click(function() {
        $(".box, .overlay").animate({
            "opacity": "0"
        }, 200, "linear", function() {
            $(".box, .overlay").remove();
        });
        $(".container").animate({
            "opacity": "1"
        }, 200, "linear");
        $("body").css({
            "overflow-y": "scroll"
        });
    });
}

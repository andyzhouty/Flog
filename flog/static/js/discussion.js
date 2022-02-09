function backToTop() {
    $("html").animate(
        { scrollTop: 0 },
        1000
    );
}
$(function () {
    $("html").animate(
        { scrollTop: document.getElementsByTagName("body")[0].scrollHeight },
        1000
    );
    let button = $("#back-to-top");
    button.on("click", backToTop);
    $(window).on("scroll", function() {
        let visibleHeight = $(window).height();
        let scrollHeight = $(document).scrollTop();
        if (scrollHeight > visibleHeight) {
            button.fadeIn(1000);
        } else {
            button.fadeOut(1000);
        }
    });
});

var hover_timer = null;
var flash = null;
function show_profile_popover(e) {
    var $el = $(e.target);

    hover_timer = setTimeout(function () {
        hover_timer = null;
        $.ajax({
            type: 'GET',
            url: $el.data('href'),
            success: function (data) {
                $el.popover({
                    html: true,
                    content: data,
                    trigger: 'manual',
                    animation: false
                });
                $el.popover("show");
                $('.popover').on("mouseleave", function() {
                    setTimeout(function () {
                        $el.popover("hide");
                    }, 200);
                })
            },
            error: function (error) {
                toast('Server Error, please try again later.');
            }
        })
    }, 500);
}
function hide_profile_popover(e) {
    var $el = $(e.target);

    if(hover_timer) {
        clearTimeout(hover_timer);
        hover_timer = null;
    } else {
        setTimeout(function () {
            if(!$('.popover:hover').length) {
                $el.popover("hide");
            }
        }, 200)
    }
}
function toast(body) {
    clearTimeout(flash);
    var $toast = $('#toast');
    $toast.text(body).fadeIn();
    flash = setTimeout(function () {
       $toast.fadeOut();
    }, 3000);
}

$('.profile-popover').hover(
    show_profile_popover.bind(this),
    hide_profile_popover.bind(this)
);

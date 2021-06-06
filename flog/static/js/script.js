/*
* @Author: Andy Zhou
* Copyright (c) 2020 All rights reserved
* MIT License
*/
let hover_timer = null;
let flash = null;

function show_profile_popover(e) {
    let $el = $(e.target);

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
                $('.popover').on("mouseleave", function () {
                    setTimeout(function () {
                        $el.popover("hide");
                    }, 200);
                });
            },
            error: function (error) {
                toastr.error('Server Error, please try again later.');
            }
        });
    }, 500);
}

function hide_profile_popover(e) {
    let $el = $(e.target);

    if (hover_timer) {
        clearTimeout(hover_timer);
        hover_timer = null;
    } else {
        setTimeout(function () {
            if (!$('.popover:hover').length) {
                $el.popover("hide");
            }
        }, 200);
    }
}

function update_notifications_count() {
    let $el = $('#notification-badge');
    $.get($el.data('href'), function (data) {
        if (data.count === 0) {
            $('#notification-badge').hide();
        } else {
            $el.show();
            $el.text(data.count);
        }
        if (!document.hasFocus() && data.count != 0) {
            document.title = '(' + data.count + ') ' + document.title;
        }
    });
}

function largeImage(e) {
    let element = $(e.target);
    let image_large = $('#image-large');
    image_large.attr('src', element.attr('src'));
    $('.content').addClass('shadow');
    image_large.show();
    image_large.height = $(document).height;
}

$(function () {
    $('img').addClass('image-normal');
    $("img[alt='identicon']").removeClass('image-normal');
    $('.image-normal').click(largeImage.bind(this));
    $('#image-large').click(function () {
        $('.content').removeClass('shadow');
        $('#image-large').hide();
    });
    $('table').addClass('table table-bordered');
});

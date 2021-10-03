/*
* @Author: Andy Zhou
* Copyright (c) 2020 All rights reserved
* MIT License
*/
let hoverTimer = null;
let flash = null;
const levelExperiences = {
    1: 100,
    2: 200,
    3: 350,
    4: 550,
    5: 800,
    6: 1100,
    7: 1500,
    8: 2500,
}

function show_profile_popover(e) {
    let $el = $(e.target);

    hoverTimer = setTimeout(function () {
        hoverTimer = null;
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
                $el.popover('show');
                $('.popover').on('mouseleave', function () {
                    setTimeout(function () {
                        $el.popover('hide');
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

    if (hoverTimer) {
        clearTimeout(hoverTimer);
        hoverTimer = null;
    } else {
        setTimeout(function () {
            if (!$('.popover:hover').length) {
                $el.popover('hide');
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
    $('img:not([class])').addClass('image-normal');
    $('.btn-action').addClass('btn btn-light btn-sm');
    $('.btn-action-activated').addClass('btn btn-primary btn-sm');
    $('.link-coin').hover(function () {
        $(this).children('img').attr('src', '/static/svg/pi-activated.svg');
    });
    $('.link-coin').mouseleave(function () {
        $(this).children('img').attr('src', '/static/svg/pi.svg');
    });
    $('.coin-option').click(function () {
        $(this).addClass('selected');
        $(this).siblings().removeClass('selected');
    })
    $('.coin-option .selected').click(function () {
        $(this).removeClass('selected');
    });
    $('#current-level-progress').each(function () {
        experience = $(this).data('experience');
        level = $(this).data('level');
        if ($(this).data('level') < 9) {
            $(this).css(
                'width',
                experience / levelExperiences[level] * 100 + '%'
            );
            $(this).parent().parent().append('<div>' + experience + ' / ' + levelExperiences[level] + '</div>');
        } else {
            $(this).css(
                'width',
                (experience / ((level - 8) * (level - 7) * 100 + 2500)) * 100 + '%'
            );
            $(this).parent().parent().append('<div>' + experience + ' / ' + ((level - 8) * (level - 7) * 100 + 2500) + '</div>');
        }
        
    });
    $('.coin-submit').click(function () {
        form = $(this).parent().parent();
        let postId = parseInt(form.data('post-id'));
        let selectedElement;
        for (let element of form.children().children('.coin-option')) {
            if ($(element).attr('class').split(' ').indexOf('selected') !== -1) {
                selectedElement = $(element);
                break;
            }
        }
        if (selectedElement === undefined) {
            toastr.error(form.data('error-message'));
        }
        let coins = parseInt(selectedElement.val());
        console.log({ 'coins': coins });
        $.ajax({
            type: 'POST',
            url: '/post/coin/' + postId + '/',
            data: { 'coins': coins },
            dataType: 'json',
            complete: function (xhr, status) {
                window.location.reload();
            },
            error: function (xhr, status, error) {
                if (error == "BAD REQUEST") {
                    toastr.error(error);
                }
            }
        });
    });
    $('img[alt="identicon"]').removeClass('image-normal');
    $('.image-normal').click(largeImage.bind(this));
    $('#image-large').click(function () {
        $('.content').removeClass('shadow');
        $('#image-large').hide();
    });
    $('table').addClass('table table-bordered');
});

/*
* @Author: Andy Zhou
* Copyright (c) 2020 All rights reserved
* MIT License
*/
$(function() {
    function render_time() {
        return moment($(this).data('timestamp')).format('lll');
    }

    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    )
})
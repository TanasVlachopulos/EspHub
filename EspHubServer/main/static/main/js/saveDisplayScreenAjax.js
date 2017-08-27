function saveDisplayScreenAjax(url, screenNum) {
    if (setCsrf()) {
        // disable save button
        $('#btn-save-' + screenNum).addClass('disabled');

        $.post(url, $('#setting-form-screen-' + screenNum).serialize());
    }
}

function setCsrf() {
    var cookie = null;
    if (document.cookie && document.cookie != '') {
        cookie = $.cookie('csrftoken');
    }
    if (cookie && cookie != 'undefined') {
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
            }
        });
        return true;
    }
    else {
        console.log('set CSRF token error');
        return false;
    }
}
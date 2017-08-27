function switchAjax(url, deviceId, ability) {
    if (setCsrf()) {
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'device': deviceId,
                'ability': ability,
                'state': $('#action-' + ability).prop('checked') ? 'on' : 'off'
            },
            success: function (response) {
                console.log(ability + ' status send');
            }
        });
    }
}

function buttonAjax(url, deviceId, ability, state) {
    if (setCsrf()) {
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'device': deviceId,
                'ability': ability,
                'state': state
            },
            success: function (response) {
                console.log(ability + ' status send');
            }
        });
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
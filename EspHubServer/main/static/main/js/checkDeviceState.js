function checkDeviceState(devicesJson, apiUrl, timeLimit) {
    var devices = JSON.parse(devicesJson);
    var onlineBadge = '<span class="new badge green" data-badge-caption="Online"></span>';
    var offlineBadge = '<span class="new badge red" data-badge-caption="Offline"></span>';

    devices.forEach(function (item, index) {
        $.getJSON(apiUrl + item, function (result) {
            if (!$.isEmptyObject(result)) {
                var resultTime = new Date(result['time']);
                var now = new Date();

                // if telemetry is older then timeLimit mark as offline
                if ((now - resultTime) / 1000 <= timeLimit) {
                    $('#state-badge-' + item).html(onlineBadge);
                }
                else {
                    $('#state-badge-' + item).html(offlineBadge);
                }
            }
            else {
                $('#state-badge-' + item).html(offlineBadge);
            }
        }).fail(function () {
            // show disconnect dialog
            if (connected === true) {
                Materialize.toast("Network connection lost", 10000, '', function () {connected = true});
                connected = false;
            }
            // make device offline
            $('#state-badge-' + item).html(offlineBadge);
        })
    });

    setTimeout(checkDeviceState, 15000, devicesJson, apiUrl, timeLimit);
}
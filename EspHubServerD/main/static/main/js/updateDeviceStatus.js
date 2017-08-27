function updateDeviceStatus(apiUrl, updateInterval) {

    $.getJSON(apiUrl, function (result) {
        if (!$.isEmptyObject(result)) {
            // console.log(result);

            var resultTime = new Date(result['_time'] * 1000);
            var formatedTime = resultTime.toTimeString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, "$1");

            $('#rssi').text(result['rssi']);
            $('#last-echo').text(formatedTime);
            $('#ip').text(result['ip']);
            $('#ssid').text(result['ssid']);
            $('#modal-rssi').text(result['rssi']);
            $('#modal-last-echo').text(formatedTime);
            $('#modal-ip').text(result['ip']);
            $('#modal-ssid').text(result['ssid']);
            $('#modal-mac').text(result['mac']);
            $('#modal-id').text(result['device_id']);
            $('#modal-heap').text(result['heap']);
            $('#modal-voltage').text(result['voltage']);
        }
        else {
            console.log("empty telemetry");
        }
    });

    setTimeout(updateDeviceStatus, updateInterval, apiUrl, updateInterval);
}

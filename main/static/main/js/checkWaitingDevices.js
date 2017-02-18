function checkWaitingDevices() {
    url = "/api/waiting-devices";
    var localDevices = [];
    if (localStorage.waitingDevices && typeof(Storage) !== "undefined" && localStorage != null) {
        localDevices = JSON.parse(localStorage.waitingDevices);
    }

    $.getJSON(url, function (result) {
        var loadedDevicesId = [];

        result.forEach(function (device, iteration) {
            if (localDevices.indexOf(device.id) == -1) {
                // console.log("New device");
                var $toastContent = $('<a href="/waiting-devices" style="color: inherit;">New device was found.</a>');
                Materialize.toast($toastContent, 7000);
            }
            loadedDevicesId.push(device.id);
        });

        // console.log(loadedDevicesId);
        if (typeof(Storage) !== 'undefined' && localStorage != null) {
            localStorage.waitingDevices = JSON.stringify(loadedDevicesId);
        }

    });

    setTimeout(checkWaitingDevices, 5000);
}

$(document).ready(checkWaitingDevices());

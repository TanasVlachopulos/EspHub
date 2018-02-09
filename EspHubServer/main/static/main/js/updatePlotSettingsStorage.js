/***
 * Update plot settings such as data range, data sampling, ... stored in local storage.
 * @param deviceId ID of current device.
 * @param abilityName Name of current ability.
 */
function updatePlotSettingsStorage(deviceId, abilityName) {
    var data = {};
    if (localStorage.plotSetting && typeof(Storage) !== "undefined" && localStorage !== null) {
        data = JSON.parse(localStorage.plotSetting);
    }

    console.log(abilityName);
    console.log(deviceId);

    if (data[deviceId] === undefined) {
        data[deviceId] = {};
    }
    if (data[deviceId][abilityName] === undefined) {
        data[deviceId][abilityName] = {};
    }

    data[deviceId][abilityName]['date-range'] = $('#date-range-input-' + abilityName).val();
    data[deviceId][abilityName]['summarization'] = $('#summarize-select-' + abilityName).val();
    data[deviceId][abilityName]['chart-type'] = $('#chart-type-select-' + abilityName).val();

    if (typeof(Storage) !== "undefined" && localStorage !== null) {
        localStorage.plotSetting = JSON.stringify(data);
    }
}
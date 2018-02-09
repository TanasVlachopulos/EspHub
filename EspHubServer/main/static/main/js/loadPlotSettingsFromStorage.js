function loadPlotSettingsFromStorage(deviceId) {
    if (localStorage.plotSetting && typeof(Storage) !== undefined && localStorage !== null) {
        data = JSON.parse(localStorage.plotSetting);

        if (data[deviceId] !== undefined){
            $.each(data[deviceId], function (abilityName, values) {
                $('#date-range-input-' + abilityName).val(values['date-range']);
                console.log(values['summarization']);
                $('#summarize-select-' + abilityName).val(values['summarization']).attr('selected', true);
                $('#chart-type-select-' + abilityName).val(values['chart-type']);
            })
        }
    }
}
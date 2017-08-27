/***
 * Handle selection in display device menu
 * @param apiUrl - Form target view
 * @param deviceName - User name of source device
 * @param abilityUserName - User name of source ability
 * @param abilityName - ID name of source ability
 * @param deviceId - ID of source device
 * @param displayNum - local tab ID
 */
function displaySelectAbility(apiUrl, deviceName, abilityUserName, abilityName, deviceId, displayNum) {
    // $('#circle-loader').show(); // show circle loader
    $('#device-name-label-' + displayNum).text(deviceName);
    $('#ability-name-label-' + displayNum).text(abilityUserName);

    // set form
    $('#data-source-device-' + displayNum).val(deviceId);
    $('#data-source-ability-' + displayNum).val(abilityName);

    // enabled save button
    $('#btn-save-' + displayNum).removeClass('disabled');

    // get plot preview
    $.get(apiUrl, function (data) {
        $('#circle-loader-' + displayNum).hide();
        // is necessary upload whole div, not only embed object (due to caching the contetn unchadged)
        var previewHtml = "<embed src='" + data + "'>";
        $('#plot-preview-' + displayNum).html(previewHtml);

        console.log('api response');
        // console.log(data);
    })
}
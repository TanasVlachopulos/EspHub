function displaySelectAbility(apiUrl, deviceName, abilityUserName, abilityName, deviceId, displayNum) {
    // $('#circle-loader').show(); // show circle loader
    $('#device-name-label-' + displayNum).text(deviceName);
    $('#ability-name-label-' + displayNum).text(abilityUserName);

    // set form
    $('#data-source-device-' + displayNum).val(deviceId);
    $('#data-source-ability-' + displayNum).val(abilityName);

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
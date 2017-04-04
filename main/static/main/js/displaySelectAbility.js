function displaySelectAbility(apiUrl, deviceName, abilityUserName) {
    // $('#circle-loader').show(); // show circle loader
    $('#device-name-label').text(deviceName);
    $('#ability-name-label').text(abilityUserName);

    // get plot preview
    $.get(apiUrl, function (data) {
        $('#circle-loader').hide();
        // is necessary upload whole div, not only embed object (due to caching the contetn unchadged)
        var previewHtml = "<embed src='" + data + "'>";
        $('#plot-preview').html(previewHtml);

        console.log('api response');
        // console.log(data);
    })
}
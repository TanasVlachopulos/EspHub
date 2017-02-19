function updateDeviceValues(apiUrl, refreshInterval) {

    $.getJSON(apiUrl, function (result) {

        result.forEach(function (item, index) {
            // console.log(item);

            // var resultTime = new Date(item['_time'] * 1000);
            var formatedTime = moment(item['time']).format('HH:mm:ss');

            var valueType = item['name'];
            var category = item['category'];

            // update fields in value card
            $('#value-' + valueType).text(item['value']);
            $('#time-' + valueType).text(formatedTime);

            // update fields in control card
            if (category == 'switch') {
                // check switch to ON position if last value in db is ON
                $('#action-' + valueType).prop('checked', (item['value'] == 'on'));
            }

            // update chart
            if (window.myLine != undefined && window.typeOfActiveChart == valueType) {
                var line = window.myLine;
                var length = line.data.labels.length;
                line.data.datasets[0].data[length] = parseFloat(item['value']);
                line.data.labels[length] = moment(item['time']).format('HH:mm:ss');
                line.update();
            }
        });
    });

    setTimeout(updateDeviceValues, refreshInterval, apiUrl, refreshInterval);
}
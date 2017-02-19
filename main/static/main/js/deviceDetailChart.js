function deviceDetailChart(url, valueType) {
    $.getJSON(url, function (result) {
        if (!$.isEmptyObject(result)) {
            _plotChart(result, valueType);
        }
        else {
            return null;
        }
    })
}

function _plotChart(result, valueType) {
    var formatedLabels = [];
    result['labels'].forEach(function (item, index) {
        formatedLabels.push(moment(item).format('HH:mm:ss'));
    });

    if (result) {
        var config = {
            type: result['chart_type'],
            data: {
                labels: formatedLabels,
                datasets: [{
                    label: result['data_label'],
                    backgroundColor: '#fff',
                    borderColor: result['border_color'],
                    data: result['values'],
                    fill: false,
                }]
            },
            options: {
                responsive: true,
            }
        };

        var ctx = $('#canvas-' + valueType);
        window.myLine = new Chart(ctx, config);
    }
}


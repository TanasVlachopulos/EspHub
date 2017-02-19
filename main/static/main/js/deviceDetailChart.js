function deviceDetailChart(canvasId) {
    if (window.myLine != undefined) {
        window.myLine.destroy();
    }

    var url = $('#' + canvasId)[0].attributes['data-url'].nodeValue;
    console.log(url);

    $.getJSON(url, function (result) {
        if (!$.isEmptyObject(result)) {
            _plotChart(result, canvasId);
        }
        else {
            return null;
        }
    })
}

function _plotChart(result, canvasId) {
    console.log(result);
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
                    lineTension: 0.2, // line curving
                    pointRadius: 0.5,
                    pointBorderWidth: 0.5,
                    backgroundColor: '#fff',
                    borderColor: result['border_color'],
                    data: result['values'],
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    xAxes: [{
                        ticks: {
                            autoSkip: true,
                            autoSkipPadding: 20,
                        }
                    }]
                }
            }
        };

        var ctx = $('#' + canvasId);
        window.myLine = new Chart(ctx, config);
        window.typeOfActiveChart = result['data_type'];
    }
}


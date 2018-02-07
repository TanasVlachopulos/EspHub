function deviceDetailChart(canvasId) {
    if (window.myLine != undefined) {
        window.myLine.destroy();
    }

    var url = $('#' + canvasId)[0].attributes['data-url'].nodeValue;
    url = new URI(url);
    url.addQuery("summarize", "minutely");
    url.addQuery("from_date", "04.02.2018");
    console.log(url.toString());

    $.getJSON(url.toString(), function (result) {
        if (!$.isEmptyObject(result)) {
            // _plotChart(result, canvasId);
            _eChart(result, canvasId);
        }
        else {
            console.log("Error: response is empty.");
            return null;
        }
    }).fail(function () {
        console.log("Error: HTTP request failed.");
    })
}

function _plotChart(result, canvasId) {
    var formatedLabels = [];
    result['labels'].forEach(function (item, index) {
        formatedLabels.push(moment(item).format('HH:mm'));
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

function _eChart(result, canvasId) {

    var myChart = echarts.init(document.getElementById(canvasId));

    var data = result['values'];
    var date = result['labels'];

    option = {
        tooltip: {
            trigger: 'axis',
            position: function (pt) {
                return [pt[0], '10%'];
            }
        },

        toolbox: {
            feature: {
                dataZoom: {
                    yAxisIndex: 'none'
                },
                restore: {},
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: date
        },
        yAxis: {
            type: 'value',
            boundaryGap: [0, '100%']
        },
        dataZoom: [{
            type: 'inside',
            start: 75,
            end: 100
        }, {
            start: 0,
            end: 10,
            handleSize: '80%',
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2
            }
        }],
        series: [
            {
                name: 'data content',
                type: 'line',
                smooth: true,
                symbol: 'none',
                sampling: 'average',
                itemStyle: {
                    normal: {
                        color: 'rgb(16, 70, 131)'
                    }
                },

                data: data
            }
        ]
    };

    // use configuration item and data specified to show chart
    myChart.setOption(option);
}

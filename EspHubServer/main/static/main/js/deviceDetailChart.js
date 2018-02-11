plotStyles = {
    line: {
        type: 'line',
        areaStyle: null,
        itemStyle: {
            normal: {
                color: '#fb8c00'
            }
        }
    },
    bar: {
        type: 'bar',
        areaStyle: null,
        primaryColor: '#fb8c00',
        itemStyle: {
            normal: {
                color: new echarts.graphic.LinearGradient(
                    0, 0, 0, 1,
                    [
                        {offset: 0, color: '#ffd54f'},
                        {offset: 0.5, color: '#ffb74d'},
                        {offset: 1, color: '#fb8c00'}
                    ]
                )
            },
            emphasis: {
                color: new echarts.graphic.LinearGradient(
                    0, 0, 0, 1,
                    [
                        {offset: 0, color: '#fb8c00'},
                        {offset: 0.7, color: '#ffb74d'},
                        {offset: 1, color: '#ffd54f'}
                    ]
                )
            }
        }
    },
    fill: {
        type: 'line',
        itemStyle: {
            normal: {
                color: '#fb8c00'
            }
        },
        areaStyle: {
            normal: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                    offset: 0,
                    color: '#fb8c00'
                }, {
                    offset: 1,
                    color: '#f06292'
                }])
            }
        },
        primaryColor: '#fb8c00'
    }
};

/***
 *
 * @param canvasId
 */
function deviceDetailChart(canvasId) {
    if (window.myLine != undefined) {
        window.myLine.destroy();
    }

    var summarization = $('#summarize-select-' + canvasId).val();
    var plotType = $('#chart-type-select-' + canvasId).val();

    var url = $('#canvas-tab-' + canvasId)[0].attributes['data-url'].nodeValue;
    url = new URI(url);
    url.addQuery("summarize", summarization);

    var dateRange = $('#date-range-input-' + canvasId).val();
    if (dateRange !== "") {
        var dateRangeSplit = dateRange.split("–");
        url.addQuery("from_date", dateRangeSplit[0]);
        url.addQuery("to_date", dateRangeSplit[1]);
    }

    args = plotStyles[plotType];
    args['unit'] = $('#unit-' + canvasId).text();

    $.getJSON(url.toString(), function (result) {
        if (!$.isEmptyObject(result)) {
            // _plotChart(result, canvasId);
            _eChart(result, 'canvas-tab-' + canvasId, args);
        }
        else {
            console.log("Error: response is empty.");
            return null;
        }
    }).fail(function () {
        console.log("Error: HTTP request failed.");
    })
}

function _eChart(result, canvasId, args) {

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
            left: 'center',
            feature: {
                dataZoom: {
                    title: {
                        zoom: 'Zoom area',
                        back: 'Zoom out area'
                    },
                    yAxisIndex: 'none'
                },
                restore: {
                    title: 'Restore'
                },
                saveAsImage: {
                    title: 'Save as png'
                }
            }
        },
        xAxis: {
            type: 'category',
            name: 'time',
            boundaryGap: false,
            data: date
        },
        yAxis: {
            name: args.unit || "",
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
                name: 'value [' + (args.unit || "") + ']',
                type: args.type || 'line',
                smooth: true,
                symbol: 'none',
                sampling: 'average',
                itemStyle: args.itemStyle || null,
                areaStyle: args.areaStyle || null,

                data: data
            }
        ]
    };

    // use configuration item and data specified to show chart
    myChart.setOption(option);
}

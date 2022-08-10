class ChartsGenerator{
    constructor(){
    }

    createOrUpdateDashboard(dashboard, dom_id) {
        this.addDashboardTitle(dashboard.title, dashboard.id, dom_id);
        dashboard.charts.forEach(function(chart_data){
            var chart = this.generateChart(dashboard.id, chart_data);
        }.bind(this));
    }

    addDashboardTitle(title, id, dom_id) {
        if (!document.getElementById(id)) {
            $(dom_id).append(
                `<div id="` + id + `" class="dashboard">
                    <div class="title">
                        <h2>` + title + `</h2>
                    </div>
                    <div id="` + id + `_charts" class="charts">
                    </div>
                </div>`
            );
        }
    }

    generateChart(dashboard_id, chart) {
        var chartId = dashboard_id + '_' + chart.id;
        if (!document.getElementById(chartId)) {
            if(chart.type != "Dataset"){
                $('#' + dashboard_id + '_charts').append(
                    `<div class="chart_area">
                         <div class="chart_container  chart_panel">
                             <div id="` + chartId + `" class="chart_data"></div>
                          </div>
                    </div>`
               );
            }else {
                $('#' + dashboard_id + '_charts').append(
                    `<div class="chart_area">
                         <div class="chart_container  chart_panel " style="padding:15px">
                            <table id="` + chartId + `" class="table table-striped" style="width:100%"></table>
                          </div>
                    </div>`
               );
            }
            

            if(chart.type == "MapChart")
                echarts.registerMap(chart.map_id, { geoJson: chart.geo_json });
        }
    
        var option = {};
        switch (chart.type) {
            case "XYChart":
                option = this.generateXYOption(chart);
                break;
            case "MapChart":
                option = this.generateMapOption(chart);
                break;
            case "HeatmapChart":
                option = this.generateHeatmapOption(chart);
                break;
            case "Dataset":
                this.generateDataset(chart, chartId);
                return;
            default:
                option = this.generateBaseOption(chart);
                break;
        }
        
        var chartDom = document.getElementById(chartId);
        var eChart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
        eChart.setOption(option, true);
    }

    generateDataset(chart, chartId){
        var table = $('#' + chartId).DataTable({
            data: chart.data,
            columns: chart.columns,
            scrollX: true,
            scrollY: 300,
            paging: false,
            "language": {
                "info": "",
                "infoFiltered": "_TOTAL_ on _MAX_ displayed"
              }
        });
    }
    
    generateBaseOption(chart){
        var option = {
            title: {
                text: chart.title,
                subtext: chart.subtitle,
                left: "center"
            },
            legend: {
                show: false,
                type: 'scroll',
                top: 'bottom'
            },
            label: {
                show: false
            },
            tooltip: {
                trigger: 'item'
            },
            series: chart.series
        };
        
        return option;
    }

    generateXYOption(chart){
        var option = {
            title: {
                text: chart.title,
                subtext: chart.subtitle,
                left: "center"
            },
            legend: {
                show: false,
                type: 'scroll',
                top: 'bottom'
            },
            tooltip: {
                trigger: 'item'
            },
            xAxis: [{
                type: chart.x_type,
                show: true,
                data: chart.x_axis_values
            }],
            yAxis: [{
                type: chart.y_type,
                show: true,
                data: chart.y_axis_values
            }],
            dataZoom: chart.dataZoom,
            series: chart.series,
        };
                
        return option;
    }
    
    generateHeatmapOption(chart){
        var option = {
            title: {
                text: chart.title,
                subtext: chart.subtitle,
                left: "center"
            },
            legend: {
                show: false,
                type: 'scroll',
                top: 'bottom'
            },
            tooltip: {
                trigger: 'item'
            },
            xAxis: [{
                type: chart.x_type,
                show: true,
                data: chart.x_axis_values,
                splitArea: {
                  show: true
                }
            }],
            yAxis: [{
                type: chart.y_type,
                show: true,
                data: chart.y_axis_values,
                splitArea: {
                  show: true
                }
            }],
            visualMap: {
                min: chart.min,
                max: chart.max,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
            },
            dataZoom: chart.dataZoom,
            series: chart.series,
        };
        
        console.log(JSON.stringify(option));
        
        return option;
    }

    generateMapOption(chart){
        var option = {
            title: {
                text: chart.title,
                subtext: chart.subtitle,
                left: "center"
            },
            visualMap: {
                min: chart.min,
                max: chart.max,
                realtime: false,
                calculable: true
            },
            series: chart.series
        };
        
        return option;
    }
}

charts_generator = new ChartsGenerator();
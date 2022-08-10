import pandas as pd

class Dashboard:
    def __init__(self, title, charts, id=None):
        self.title = title
        self.charts = charts
        if id is not None:
            self.id = id
        else:
            self.id = ''.join(e for e in self.title if e.isalnum())


class Chart:
    def __init__(self, graph_title, chart_type, series, id=None, graph_subtitle=None):
        self.title = graph_title
        self.subtitle = graph_subtitle
        self.series = series
        self.type = chart_type
        if id is not None:
            self.id = id
        else:
            self.id = ''.join(e for e in self.title if e.isalnum())



class BaseChart(Chart):
    def __init__(self, graph_title, series, id=None, graph_subtitle=None):
        Chart.__init__(self, graph_title, 'BaseChart', series, id, graph_subtitle)

class XYChart(Chart):
    def __init__(self, graph_title, x_type, y_type, series, x_axis_values=None, y_axis_values=None, id=None,
                 graph_subtitle=None):
        Chart.__init__(self, graph_title, 'XYChart', series, id, graph_subtitle)
        self.x_type = x_type  # either 'value', 'category', 'time', 'log'
        self.y_type = y_type  # either 'value', 'category', 'time', 'log'
        self.x_axis_values = x_axis_values
        self.y_axis_values = y_axis_values

class HeatmapChart(Chart):
    def __init__(self, graph_title, series, x_axis_values, y_axis_values, min, max, id=None, graph_subtitle=None):
        Chart.__init__(self, graph_title, 'HeatmapChart', series, id, graph_subtitle)
        self.x_type = 'category'
        self.y_type = 'category'
        self.x_axis_values = x_axis_values
        self.y_axis_values = y_axis_values
        self.min = min
        self.max = max

class MapChart(Chart):
    def __init__(self, graph_title, series, map_id, geo_json, legend_min=None, legend_max=None, id=None,
                 graph_subtitle=None):
        Chart.__init__(self, graph_title, 'MapChart', series, id, graph_subtitle)
        self.map_id = map_id
        self.geo_json = geo_json
        if legend_min is not None:
            self.min = legend_min
        else:
            self.min = min([x['value'] for x in series.data])
        if legend_max is not None:
            self.max = legend_max
        else:
            self.max = max([x['value'] for x in series.data])




class Series:
    def __init__(self, data, legend_name=None):
        self.name = legend_name
        self.data = data

class LineSeries(Series):
    def __init__(self, data, legend_name=None, stack=None):
        Series.__init__(self, data, legend_name)
        # data is either [x, y, ..], or [[x, y], ..]
        self.type = 'line'
        if stack is not None:
            self.stack = 'Total'

class BarSeries(Series):
    def __init__(self, data, legend_name=None, stack=None):
        Series.__init__(self, data, legend_name)
        # data is either [x, y, ..], or [[x, y], ..]
        self.type = 'bar'
        if stack is not None:
            self.stack = 'Total'

class ScatterSeries(Series):
    def __init__(self, data, legend_name=None, stack=None):
        Series.__init__(self, data, legend_name)
        # data is either [x, y, ..], or [[x, y], ..]
        self.type = 'scatter'

class PieSeries(Series):
    def __init__(self, slice_names, slice_values):
        data = [{'name': slice_names[i], 'value': slice_values[i]} for i in range(len(slice_names))]
        Series.__init__(self, data)
        self.type = 'pie'
        self.radius = '50%'
        self.minShowLabelAngle = '5'

class GeoDensitySeries(Series):
    def __init__(self, item_names, item_values, map_id):
        data = [{'name': item_names[i], 'value': item_values[i]} for i in range(len(item_names))]
        Series.__init__(self, data)
        self.type = 'map'
        self.map = map_id

class GaugeSeries(Series):
    def __init__(self, value, min_gauge, max_gauge, label=None):
        if label is not None:
            data = [{'name' : label, 'value' : value}]
        else:
            data = [{'name' : label}]
        Series.__init__(self, data)
        self.type = 'gauge'
        self.min = int(min_gauge)
        self.max = int(max_gauge)

class SankeySeries(Series):
    def __init__(self, sources, targets, values):
        nodeSet = set(sources)
        nodeSet.update(targets)
        data = [{'name': item} for item in nodeSet]
        Series.__init__(self, data)
        self.type = 'sankey'
        self.links = [{'source': source, 'target': target, 'value': value} for source, target, value in zip(sources, targets, values)]
        self.tootlip = { 'trigger': 'item', 'triggerOn': 'mousemove'}

class HeatmapSeries(Series):
    def __init__(self, data):
        Series.__init__(self, data)
        self.type = 'heatmap'

class Dataset():
    def __init__(self, dataframe, title, id=None):
        self.title = title
        self.type = "Dataset"
        self.data = dataframe.values.tolist()
        self.columns = [{ 'title' : x} for x in dataframe.columns.tolist()]
        if id is not None:
            self.id = id
        else:
            self.id = ''.join(e for e in self.title if e.isalnum())


def generateStackedSeries(dataframe, name_column, x_column, y_column, aggregation, type=None, limit=50):
    # get top N elements to comply with the limit 
    top_n = (dataframe.groupby([name_column], as_index=False)[y_column]
                            .agg({'agg':aggregation})
                            .fillna(0)
                            .sort_values('agg', ascending=False)
                            .head(limit)[name_column]
                            .tolist())
    dataframe.loc[~dataframe[name_column].isin(top_n), name_column] = 'Others'

    #df_pivoted = dataframe.pivot_table(index=x_column, columns=name_column, values=y_column, aggfunc=aggregation).fillna(0)
    df_pivoted = dataframe.groupby([x_column, name_column], sort=False).agg({y_column:[aggregation]}).unstack(level=name_column).fillna(0) #same but quicker
    
    series = []
    x_values = df_pivoted.index.tolist()
    for column in df_pivoted.columns:
        if type is not None and type=='line':
            series.append(LineSeries(list(zip(x_values, df_pivoted[column])), legend_name = column[2], stack = True))
        else:
            series.append(BarSeries(list(zip(x_values, df_pivoted[column])), legend_name = column[2], stack = True))

    return series

def generateHeatmapChart(dataframe, x_column, y_column, value_column, aggregation, title, x_values = None, y_values = None, subtitle = None):
    df_heatmap = dataframe.groupby([x_column, y_column], sort=False).agg({value_column:[aggregation]}).unstack(level=y_column).fillna(0)
    if not x_values:
        x_values = list(set(dataframe[x_column]))
    if not y_values:
        y_values = list(set(dataframe[y_column]))
    triplets = []
    min_value = df_heatmap.iat[0,0]
    max_value = df_heatmap.iat[0,0]
    for index, row in df_heatmap.iterrows():
        for column in df_heatmap.columns:
            triplets.append([x_values.index(index), y_values.index(column[2]), row[column]])
            min_value = min(min_value, row[column])
            max_value = max(max_value, row[column])
    heatmap_series = HeatmapSeries(triplets)
    return HeatmapChart(title, heatmap_series, x_values, y_values, min_value, max_value, graph_subtitle = subtitle)
   
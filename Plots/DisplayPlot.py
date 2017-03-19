import pygal as pygal


class DisplayPlot(object):
    def __init__(self, values, x_labels=None, type='line', x_title=None, y_title=None, title=None, color=None,
                 show_dots=False, show_legend=False, x_label_rotation=0):

        self.config = pygal.Config(show_dots=show_dots, show_legend=show_legend, x_label_rotation=x_label_rotation)

        self.chart = None
        if type == 'line':
            self.chart = pygal.Line(self.config)

        self.chart.x_labels = x_labels
        self.chart.add('line', values)

    def render_to_base64(self, width=None, height=None):
        if width and height:
            return self.chart.render_data_uri(width=width, height=height)
        else:
            return self.chart.render_data_uri()

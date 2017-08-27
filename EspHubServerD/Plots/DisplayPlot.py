import pygal as pygal


class DisplayPlot(object):
    def __init__(self, values, x_labels=None, type='line', x_title=None, y_title=None, title=None, color=None,
                 show_dots=False, show_legend=False, x_label_rotation=0):
        """
        Generate plot for remote display
        :param values: 
        :param x_labels: 
        :param type: 
        :param x_title: 
        :param y_title: 
        :param title: 
        :param color: 
        :param show_dots: 
        :param show_legend: 
        :param x_label_rotation: 
        """

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

    def render_to_png(self, filename, width=None, height=None):
        try:
            import cairosvg
            if width and height:
                return self.chart.render_to_png(filename, width=width, height=height)
            else:
                return self.chart.render_to_png(filename)
        except OSError:
            print("Error loading module cairosvg (convert svg plot to png file)")

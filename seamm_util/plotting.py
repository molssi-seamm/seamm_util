# -*- coding: utf-8 -*-

"""
A package for handling plotly plots in SEAMM.

A figure comprises one or more plots (or graphs) laid out in a grid.
The datasets within a plot are represetned by traces, lines, scatter
plots, pie chart elements, etc.

This package consists of a Figure class which is a container, a Plot
class that handles the actual plotting, and a Trace class for the
individual datasets and their graphical representations. The figure
class uses a grid similar to the Tk grid to control the layout of the
plots.

This package does not directly interact with plotly. Rather, it uses templates
and Jinja to create the JSON, HTML or other representation of a plotly figure.
The various containers in this package contain dictionaries of Jinja keys and
the associated values. The keys needed are defined by the template used.
"""

from .dictionary import Dictionary
import json


class Figure(Dictionary):
    """Holds one or more subplots and controls the layout."""

    def __init__(self, *args, jinja_env=None, template=None, **kwargs):
        """Initialize a figure.

        Keyword arguments:
        """

        super().__init__(*args, **kwargs)

        self._jinja_env = jinja_env
        self._template = template
        self._plots = Dictionary(ordered=True)

        self._grid = {"nrows": 0, "ncolumns": 0, "plots": {}, "layout": {}}

    @property
    def template(self):
        """The template to use for this figure."""
        return self._template

    @template.setter
    def template(self, value):
        self._template = value

    def add_plot(self, name, **kwargs):
        """Create a new plot and return it.

        Parameters
        ----------
        name : str
            The name of the plot, which must be unique.

        Returns
        -------
        The plot object.
        """
        if name in self._plots:
            raise KeyError("Plot '{}' already exists.".format(name))

        self._plots[name] = Plot(**kwargs)

        return self._plots[name]

    def get_plot(self, name):
        """Return the named plot.

        Parameters
        ----------
        name : str
            The name of the plot, which must exist.

        Returns
        -------
        The plot object.
        """
        if name not in self._plots:
            raise KeyError("Plot '{}' does not exist.".format(name))

        return self._plots[name]

    def grid_plots(self, *args, padx=0.02, pady=0.02):
        """Define the layout of the plots.

        When there is more than one plot, they need to be laid out in a grid.
        This method is called to define the layout, and will follow closely the
        approach used in Tk grid.

        Parameters
        ----------
        *args
            Positional arguments specifying the layout of one or more rows.
            each row is given as a string composed of the following:

                <plot> :
                     is the name of a plot.

                x :
                    leaves an empty column between the plot on the
                    left and the plot on the right.

                ^ :
                    extends the row span of the plot above the ^'s in the
                    grid. The number of ^'s in a row must match the number
                    of columns spanned by the plot above it.

                - :
                    increases the column span of the plot to the
                    left. Several -'s in a row will successively increase
                    the number of columns spanned. A - may not follow a ^
                    or a x, nor may it be the first plot argument to
                    grid configure.

        **kwargs
            Keyword arguments for options for the given rows:
                padx : float, optional
                    The fraction of space to leave between plots in a row.
                    Defaults to 0.02.
                pady : float, optional
                    The fraction of space to leave between rows. Defaults to
                    0.02.
        """

        grid = self._grid
        grid["padx"] = padx
        grid["pady"] = pady
        plots = grid["plots"] = []
        # First, check that the layout is valid
        last = ""
        for row_spec in args:
            column = 0
            for key in row_spec.split():
                if column == 0:
                    if key == "-":
                        raise RuntimeError(
                            "'-' cannot be the first item in a row: '{}'".format(
                                row_spec
                            )
                        )
                else:
                    if key == "-" and (last == "^" or last == "x"):
                        raise RuntimeError(
                            "'-' cannot follow 'x' or '^': '{}'".format(row_spec)
                        )
                last = key
                if key in "-^x":
                    pass
                else:
                    if key in plots:
                        raise RuntimeError(
                            r"Plot '{}' is already used: '{}'".format(key, row_spec)
                        )
                    plots.append(key)
                column += 1

        # Now process the entire specification
        layout = grid["layout"]
        for row_spec in args:
            row = grid["nrows"]
            grid["nrows"] += 1
            column = 0
            for key in row_spec.split():
                layout[(row, column)] = key
                column += 1
            if column > grid["ncolumns"]:
                grid["ncolumns"] = column

        # Get row and column spans for the plots, checking that the input
        # is valid

        nrows = grid["nrows"]
        ncolumns = grid["ncolumns"]
        plots = grid["plots"] = []
        for row in range(nrows):
            for column in range(ncolumns):
                name = layout[(row, column)]
                if name not in "-^x":
                    plot = self.get_plot(name)
                    plot.row = row
                    plot.column = column
                    plot.column_span = 1

                    plots.append(plot)

                    # Walk to the right looking for cells with '-'
                    for tmp in range(column + 1, ncolumns):
                        if layout[(row, tmp)] == "-":
                            plot.column_span += 1
                        else:
                            break
                    plot.row_span = 1
                    for tmp in range(row + 1, nrows):
                        # Walk down looking for cell with '^'
                        if layout[(tmp, column)] == "^":
                            plot.row_span += 1

                            # If the plot spans columns and rows, all the
                            # cells in the extra rows must be '^'.
                            # Check this!
                            for col in range(column + 1, column + plot.column_span):
                                if layout[(tmp, col)] != "^":
                                    val = layout[(tmp, col)]
                                    raise RuntimeError(
                                        (
                                            "The cell at {},{} should be a"
                                            " '^', not '{}'"
                                        ).format(tmp, col, val)
                                    )
                        else:
                            break

    def dump(self, filename):
        """Write the filled in template to disk as <filename>.

        Parameters
        ----------
        filename : str or filepath
            The name or path to the file to write.

        Returns
        -------
        nothing
        """

        text = self.dumps()
        with open(filename, "w") as fd:
            fd.write(text)

    def dumps(self):
        """Return the filled in template document as a string.

        Merge the layout data and the traces into the template document and
        return a string version of the document.

        Returns
        -------
        str
            The resulting document.
        """
        # Ensure that the jsonify filter is available in Jinja

        if "jsonify" not in self._jinja_env.filters:
            self._jinja_env.filters["jsonify"] = json.dumps

        # Get the layout (or create a default if there isn't one)
        # In the process get a list of the plots...
        plots = []
        grid = self._grid

        if len(grid["layout"]) == 0:
            # Set up the default layout of a vertical column of subplots
            nrows = 0
            ncolumns = 1
            layout = {}
            for plot in self._plots.values():
                plots.append(plot)
                layout[(nrows, 0)] = plot
                plot.row = nrows
                plot.column = 0
                nrows += 1
            padx = 0.02
            pady = 0.02
        else:
            nrows = grid["nrows"]
            ncolumns = grid["ncolumns"]
            plots = grid["plots"]
            padx = grid["padx"]
            pady = grid["pady"]

        # Work out where the plots (or really their axes) go
        width = 1.0 / ncolumns
        height = 1.0 / nrows

        for plot in plots:
            row = plot.row
            column = plot.column
            row_span = plot.row_span
            column_span = plot.column_span

            if row == 0:
                top = 1.0
            else:
                top = 1 - row * height - pady

            left = column * width
            if column + column_span == ncolumns:
                right = 1.0
            else:
                right = left + column_span * width - padx
            bottom = 1 - (row + row_span) * height

            plot.left = left
            plot.right = right
            plot.top = top
            plot.bottom = bottom

        # Number the axes sequentially and set their limits
        axis_number = 1
        for plot in plots:
            for axis in plot.axes:
                xyz = axis.direction
                axis.update(
                    {
                        "number": axis_number,
                        "name": xyz + "axis" + str(axis_number),
                        "short_name": xyz + str(axis_number),
                    }
                )
                if xyz == "x":
                    axis.update({"start": plot.left, "stop": plot.right})
                elif xyz == "y":
                    axis.update({"start": plot.bottom, "stop": plot.top})
                axis_number += 1

        # Sort out any anchors between axes and get the data
        axes = []
        for plot in plots:
            for axis in plot.axes:
                if axis.anchor is None:
                    axis.update(anchor="free")
                else:
                    axis.update(anchor=axis.anchor["short_name"])

                axes.append(axis.to_dict())

        # And, finally, set up the traces
        traces = []
        for plot in plots:
            for trace in plot.values():
                if trace.x_axis is not None:
                    trace.update(xaxis=trace.x_axis["short_name"])
                if trace.y_axis is not None:
                    trace.update(yaxis=trace.y_axis["short_name"])
                if trace.z_axis is not None:
                    trace.update(zaxis=trace.z_axis["short_name"])

                traces.append(trace.to_dict())

        # Assemble all the data and pass to Jinja
        tmp = dict(self)
        tmp["traces"] = traces
        tmp["axes"] = axes

        template = self._jinja_env.get_template(self.template)
        result = template.render(tmp)

        return result


class Plot(Dictionary):
    """Class to represent a plotly plot.

    The Plot class contains Axes and Traces, which represent the
    datasets being plotted.  This class is a dict-like object where
    the elements of the dictionary are the traces.
    """

    def __init__(
        self,
        left=0,
        right=1,
        top=1,
        bottom=0,
        row=0,
        column=0,
        column_span=1,
        row_span=1,
    ):
        """Initialize a plot, optionally with data.

        Keyword arguments:
        """
        super().__init__(ordered=True)

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.row = row
        self.column = column
        self.column_span = column_span
        self.row_span = row_span

        self._axes = []

    @property
    def axes(self):
        """The list of axes for this plot."""
        return self._axes

    def add_axis(self, direction, anchor=None, **kwargs):
        """Create a new axis and return it.

        Parameters
        ----------
        direction : str (one of 'x', 'y', or 'z')
            The direction of this axis.

        Returns
        -------
        The axis object.
        """
        axis = Axis(direction, anchor=anchor, **kwargs)
        self._axes.append(axis)
        return axis

    def add_trace(self, name, x_axis=None, y_axis=None, z_axis=None, **kwargs):
        """Create a new trace and return it.

        Parameters
        ----------
        name : str
            The name of the trace, which must be unique.

        Returns
        -------
        The trace object.
        """
        if name in self:
            raise KeyError("Trace '{}' already exists.".format(name))

        self[name] = Trace(
            x_axis=x_axis, y_axis=y_axis, z_axis=z_axis, name=name, **kwargs
        )

        return self[name]


class Axis(Dictionary):
    """Class to represent an axis in a plotly plot.

    The Axis class defines an axis and the  associated graphical
    control for how to display them. The class is a dict-like object
    where the elements of the dictionary are the control parameters
    for the axis.
    """

    def __init__(self, direction, *args, anchor=None, **kwargs):
        """Initialize an axis, optionally with data.

        Parameters
        ----------
        direction : str (one of 'x', 'y', or 'z')
            The direction for this axis

        args : dict
            0+ dictionaries to update from, in order

        kwargs : keyword - value pairs
            0+ named arguments to update from
        """
        super().__init__(ordered=True)

        self.anchor = anchor
        self.direction = direction
        self["label"] = ""
        self["number"] = None
        self["start"] = 0.0
        self["stop"] = 1.0

        self.update(*args, **kwargs)

    def to_dict(self):
        """Return a dictionary representing the axis.

        Returns
        -------
        dict
            A dictionary of the axis data, suitable for Jinja.
        """
        return dict(self.data)


class Trace(Dictionary):
    """Class to represent a trace in a plotly plot.

    The Trace class contains the datasets and associated graphical
    control for how to display them. The class is a dict-like object
    where the elements of the dictionary are the traces.
    """

    def __init__(self, x_axis=None, y_axis=None, z_axis=None, **kwargs):
        """Initialize a trace, optionally with data.

        Keyword arguments:
        args : dict
            0+ dictionaries to update from, in order
        kwargs : keyword - value pairs
            0+ named arguments to update from
        """
        super().__init__(**kwargs)

        self.x_axis = x_axis
        self.y_axis = y_axis
        self.z_axis = z_axis

    def to_dict(self):
        """Return a dictionary representing the trace.

        Returns
        -------
        dict
            A dictionary of the trace data, suitable for Jinja.
        """
        return dict(self.data)

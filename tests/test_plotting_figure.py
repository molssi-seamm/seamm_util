#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_util` package, plotting module."""

import pytest
from seamm_util import Figure
import sys


def test_create():
    """Testing that we can create a Figure object."""
    fig = Figure()
    assert str(type(fig)) == "<class 'seamm_util.plotting.Figure'>"


def test_set_get_item():
    """Testing setting and then getting an item."""
    fig = Figure()
    fig["a"] = 53
    assert fig["a"] == 53


def test_len():
    """Testing getting the length of a dictionary."""
    fig = Figure()
    fig["a"] = 53
    assert len(fig) == 1


def test_del_item():
    """Testing that we can delete an item."""
    fig = Figure()
    fig["a"] = 53
    del fig["a"]
    assert len(fig) == 0


def test_iter():
    """Testing that we can iterate over a Figure."""
    fig = Figure(ordered=True)
    fig.update({"a": 1, "b": 2, "c": 3})
    keys = []
    for key in fig:
        keys.append(key)

    assert keys == ["a", "b", "c"]


def test_str():
    """Testing that we can get a str representation."""
    fig = Figure(ordered=True)
    fig.update(a=1, b=2, c=3)
    if sys.version_info >= (3, 7):
        assert str(fig) == "{'a': 1, 'b': 2, 'c': 3}"
    else:
        assert str(fig) == "OrderedDict([('a', 1), ('b', 2), ('c', 3)])"


def test_repr():
    """Testing that we can get an official representation."""
    fig = Figure(ordered=True)
    fig.update(a=1, b=2, c=3)
    if sys.version_info >= (3, 7):
        assert repr(fig) == "{'a': 1, 'b': 2, 'c': 3}"
    else:
        assert repr(fig) == "OrderedDict([('a', 1), ('b', 2), ('c', 3)])"


def test_fromkeys():
    """Test the class method fromkeys."""
    fig = Figure.fromkeys(["a", "b", "c"], 1)
    assert repr(fig) == "{'a': 1, 'b': 1, 'c': 1}"


def test_copy():
    """Testing that we can get an official representation."""
    fig = Figure(ordered=True)
    fig.update(a=1, b=2, c=3)

    e = fig.copy()
    fig["b"] = 10

    if sys.version_info >= (3, 7):
        assert str(e) == "{'a': 1, 'b': 10, 'c': 3}"
    else:
        assert str(e) == "OrderedDict([('a', 1), ('b', 10), ('c', 3)])"


def test_template_attribute():
    """Test that we can get the template as an attribute."""
    fig = Figure(template="My Template")

    assert fig.template == "My Template"


def test_set_template_attribute():
    """Test that we can set the template as an attribute."""
    fig = Figure(template="My Template")
    fig.template = "A different template"

    assert fig.template == "A different template"


def test_get():
    """Test that we can 'get' an existing element."""
    fig = Figure({"a": 1, "b": 2, "c": 3})

    assert fig.get("b") == 2


def test_get_default():
    """Test that we 'get' the default for a missing element."""
    fig = Figure({"a": 1, "b": 2, "c": 3})

    assert fig.get("missing") is None


def test_get_default_value():
    """Test that we 'get' the default for a missing element."""
    fig = Figure({"a": 1, "b": 2, "c": 3})

    assert fig.get("missing", "default") == "default"


def test_add_plot():
    """Test that we can add a plot."""
    fig = Figure({"a": 1, "b": 2, "c": 3})
    plot1 = fig.add_plot("plot1")
    assert str(type(plot1)) == "<class 'seamm_util.plotting.Plot'>"


def test_adding_duplicate_plot():
    """Test that adding a duplicate plot raises an error."""
    fig = Figure({"a": 1, "b": 2, "c": 3})
    plot1 = fig.add_plot("plot1")  # noqa: F841
    with pytest.raises(KeyError, match=r"Plot 'plot1' already exists."):
        plot2 = fig.add_plot("plot1")  # noqa: F841


def test_get_plot():
    """Test that we can get an existing plot."""
    fig = Figure({"a": 1, "b": 2, "c": 3})
    plot1 = fig.add_plot("plot1")  # noqa: F841
    plot1a = fig.get_plot("plot1")
    assert str(type(plot1a)) == "<class 'seamm_util.plotting.Plot'>"


def test_getting_missing_plot():
    """Test that getting a missing plot raises an error."""
    fig = Figure({"a": 1, "b": 2, "c": 3})
    plot1 = fig.add_plot("plot1")  # noqa: F841
    with pytest.raises(KeyError, match=r"Plot 'plot2' does not exist."):
        plot2 = fig.get_plot("plot2")  # noqa: F841


def test_grid_error1():
    """Test the gridding of plots, error with initial '-'."""
    fig = Figure()
    with pytest.raises(RuntimeError, match=r"'-' cannot be the first item.*"):
        fig.grid_plots(
            "plot1 plot2 plot3 plot4",
            "  -     -     -     x  ",
            "  ^     ^     ^   plot6",
        )  # yapf: disable


def test_grid_error2():
    """Test the gridding of plots, error with '-' following '^' or 'x'."""
    msg = r"'-' cannot follow 'x' or '^': '  ^     -     ^   plot6'"

    fig = Figure()
    with pytest.raises(RuntimeError) as e:
        fig.grid_plots(
            "plot1 plot2 plot3 plot4",
            "plot5   -     -     x  ",
            "  ^     -     ^   plot6",
        )  # yapf: disable
    assert msg in str(e)


def test_grid_error3():
    """Test the gridding of plots, error with duplicate plots."""
    msg = r"Plot 'plot6' is already used: '  ^     ^     ^   plot6'"

    fig = Figure()
    with pytest.raises(RuntimeError) as e:
        fig.grid_plots(
            "plot1 plot2 plot3 plot4",
            "plot6   -     -     x  ",
            "  ^     ^     ^   plot6",
        )  # yapf: disable
    assert msg in str(e)


def test_grid_error4():
    """Test the gridding of plots, error with rowspan."""
    msg = r"The cell at 2,2 should be a '^', not 'plot7'"

    fig = Figure()
    fig.add_plot("plot1")
    fig.add_plot("plot2")
    fig.add_plot("plot3")
    fig.add_plot("plot4")
    fig.add_plot("plot5")
    fig.add_plot("plot6")
    fig.add_plot("plot7")
    with pytest.raises(RuntimeError) as e:
        fig.grid_plots(
            "plot1 plot2 plot3 plot4",
            "plot6   -     -     x  ",
            "  ^     ^   plot7   -  ",
        )  # yapf: disable
    assert msg in str(e)

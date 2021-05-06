#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_util` package, plotting module."""

from seamm_util import Figure
import jinja2
import os

# import pytest

# Create the Jinja environment with the path we want
results_path = os.path.join(os.path.dirname(__file__), "results")
template_path = os.path.join(os.path.dirname(__file__), "templates")
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))


def test_simple_plot():
    """Testing that we can create a simple plot."""
    fig = Figure(jinja_env=env, template="line.html_template", title="Simple plot")

    plot = fig.add_plot("Energies")

    x_axis = plot.add_axis("x", label="Time (ps)")
    y_axis = plot.add_axis("y", label="Energy (kcal/mol)", anchor=x_axis)
    x_axis.anchor = y_axis

    plot.add_trace(
        x_axis=x_axis,
        y_axis=y_axis,
        name="Total",
        showlegend="false",
        x0=0,
        dx=1.0,
        xlabel="t",
        xunits="ps",
        y=[110.0, 111.0, 110.0, 109.0, 110.0],
        ylabel="E",
        yunits="kcal/mol",
        color="#20a8d8",
    )

    graph = fig.dumps()

    results_file = os.path.join(results_path, "simple_plot.html")
    try:
        with open(results_file, "r") as fd:
            correct_result = fd.read()
    except Exception:
        correct_result = ""

    if graph != correct_result:
        with open(results_file + "+", "w") as fd:
            fd.write(graph)

    assert graph == correct_result


def test_two_plots():
    """Testing that we can create two plots."""
    fig = Figure(jinja_env=env, template="line.html_template", title="Two plots")

    plot1 = fig.add_plot("plot1")

    x_axis = plot1.add_axis("x", label="Time (ps)")
    y_axis = plot1.add_axis("y", label="Energy (kcal/mol)", anchor=x_axis)
    x_axis.anchor = y_axis

    plot1.add_trace(
        x_axis=x_axis,
        y_axis=y_axis,
        name="Total",
        showlegend="false",
        x0=0,
        dx=1.0,
        xlabel="t",
        xunits="ps",
        y=[110.0, 111.0, 110.0, 109.0, 110.0],
        ylabel="E",
        yunits="kcal/mol",
        color="#20a8d8",
    )

    plot2 = fig.add_plot("plot2")

    x_axis = plot2.add_axis("x", label="Time (ps)")
    y_axis = plot2.add_axis("y", label="Energy (kcal/mol)", anchor=x_axis)
    x_axis.anchor = y_axis

    plot1.add_trace(
        x_axis=x_axis,
        y_axis=y_axis,
        name="Small",
        showlegend="false",
        x0=0,
        dx=1.0,
        xlabel="t",
        xunits="ps",
        y=[10.0, 11.0, 10.0, 9.0, 10.0],
        ylabel="E",
        yunits="kcal/mol",
        color="blue",
    )

    fig.grid_plots("plot1   -     x", "  ^     ^   plot2")  # yapf: disable

    graph = fig.dumps()

    results_file = os.path.join(results_path, "two_plots.html")
    try:
        with open(results_file, "r") as fd:
            correct_result = fd.read()
    except Exception:
        correct_result = ""

    if graph != correct_result:
        with open(results_file + "+", "w") as fd:
            fd.write(graph)

    assert graph == correct_result


def test_writing_plot(tmpdir):
    """Testing that we can create write a plot to disk."""
    fig = Figure(jinja_env=env, template="line.html_template", title="Simple plot")

    plot = fig.add_plot("Energies")

    x_axis = plot.add_axis("x", label="Time (ps)")
    y_axis = plot.add_axis("y", label="Energy (kcal/mol)", anchor=x_axis)
    x_axis.anchor = y_axis

    plot.add_trace(
        x_axis=x_axis,
        y_axis=y_axis,
        name="Total",
        showlegend="false",
        x0=0,
        dx=1.0,
        xlabel="t",
        xunits="ps",
        y=[110.0, 111.0, 110.0, 109.0, 110.0],
        ylabel="E",
        yunits="kcal/mol",
        color="#20a8d8",
    )

    filename = tmpdir / "plot.html"
    fig.dump(filename)

    with open(filename, "r") as fd:
        graph = fd.read()

    results_file = os.path.join(results_path, "simple_plot.html")
    try:
        with open(results_file, "r") as fd:
            correct_result = fd.read()
    except Exception:
        correct_result = ""

    if graph != correct_result:
        with open(results_file + "+", "w") as fd:
            fd.write(graph)

    assert graph == correct_result

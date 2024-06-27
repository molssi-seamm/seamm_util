#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_util` package."""

import seamm_util
from pathlib import Path

datapath = Path(__file__).parent / "data"


def uri_handler(path):
    if str(path).startswith("data:"):
        return (datapath / str(path)[5:]).expanduser().resolve()
    else:
        return Path(path)


def test_open_1file():
    """Testing that we can read a simple file"""
    filepath = datapath / "file1.txt.gz"
    data = ["file1 line 1", "file1 line 2", "file1 line 3", "file1 line 4"]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_open_2files():
    """Testing that the default 'include' works"""
    filepath = datapath / "file_middle.txt.gz"
    data = [
        "file_middle line 1",
        "file_middle line 2",
        "file1 line 1",
        "file1 line 2",
        "file1 line 3",
        "file1 line 4",
        "file_middle line 3",
    ]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_open_uri():
    """Testing that the default 'include' works"""
    filepath = "data:file_uri.txt.gz"
    data = [
        "file_uri line 1",
        "file_uri line 2",
        "file1 line 1",
        "file1 line 2",
        "file1 line 3",
        "file1 line 4",
        "file_uri line 3",
    ]

    i = 0
    with seamm_util.Open(
        filepath, "r", include="include", uri_handler=uri_handler
    ) as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_open_2files_at_end():
    """Testing that the default 'include' works at the end of a file"""
    filepath = datapath / "file_end.txt.gz"
    data = [
        "file_end line 1",
        "file_end line 2",
        "file_end line 3",
        "file1 line 1",
        "file1 line 2",
        "file1 line 3",
        "file1 line 4",
    ]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_lines():
    """Testing the line count for each line, with an included file

    Note that the line count includes the line with 'include'
    """
    filepath = datapath / "file_middle.txt.gz"

    num = [1, 2, 1, 2, 3, 4, 4]
    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert fd.lineno == num[i]
            i += 1


def test_total_lines():
    """Testing the total number of lines with an included file

    Note that the line count includes the line with 'include'
    """
    filepath = datapath / "file_middle.txt.gz"

    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            pass
        assert fd.total_lines == 8


def test_nested_includes():
    """Testing an include within an include"""
    filepath = datapath / "file_include1.txt.gz"
    data = [
        "file_include1 line1",
        "file_end line 1",
        "file_end line 2",
        "file_end line 3",
        "file1 line 1",
        "file1 line 2",
        "file1 line 3",
        "file1 line 4",
    ]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_include_empty_file():
    """Testing that including an empty file works"""
    filepath = datapath / "include_empty_file.txt.gz"
    data = ["file_end line 1", "file_end line 2", "file_end line 3"]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_blank_lines():
    """Testing that empty lines and ones with just blanks don't
    cause any problems
    """
    filepath = datapath / "include_blank_lines.txt.gz"
    data = [
        "file_end line 1",
        "",
        "file_end line 3",
        "blank_lines first line",
        "   ",
        "",
        "blank_lines 4th line",
        "   ",
        "",
    ]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert line[0:-1] == data[i]
            i += 1


def test_stack():
    """Testing the stack of files part way through reading includes"""
    cwd = Path(__file__).parent
    filepath = datapath / "file_include1.txt.gz"
    data = [
        "data/file1.txt.gz:2",
        "data/file_end.txt.gz:4",
        "data/file_include1.txt.gz:2",
    ]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            i += 1
            if i == 6:
                stack = []
                for line in fd.stack():
                    stack.append(str(Path(line).relative_to(cwd)).lower())
                print("Stack")
                print("\t" + "\n\t".join(stack))
                print("should be")
                print("\t" + "\n\t".join(data))
                assert stack == data
                break


def test_different_include():
    """Testing that '#include' works"""
    filepath = datapath / "file_#include.txt.gz"
    data = [
        "file_middle line 1",
        "file_middle line 2",
        "file1 line 1",
        "file1 line 2",
        "file1 line 3",
        "file1 line 4",
        "file_middle line 3",
    ]

    i = 0
    with seamm_util.Open(filepath, "r", include="#include") as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_push():
    """Testing that the default 'include' works"""
    filepath = datapath / "file_middle.txt.gz"
    data = [
        "file_middle line 1",
        "file_middle line 2",
        "file1 line 1",
        "file1 line 2",
        "file1 line 3",
        "file1 line 4",
        "file_middle line 3",
        "file1 line 4",
        "file_middle line 3",
    ]

    i = 0
    with seamm_util.Open(filepath, "r", include="include") as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1
            if i == 7:
                fd.push(2)

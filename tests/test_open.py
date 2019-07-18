#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_util` package."""

import seamm_util
import os
import os.path


def test_open_1file():
    """Testing that we can read a simple file
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file1.txt')
    data = ['file1 line 1', 'file1 line 2', 'file1 line 3', 'file1 line 4']

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_open_2files():
    """Testing that the default 'include' works
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file_middle.txt')
    data = [
        'file_middle line 1', 'file_middle line 2', 'file1 line 1',
        'file1 line 2', 'file1 line 3', 'file1 line 4', 'file_middle line 3'
    ]

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_open_2files_at_end():
    """Testing that the default 'include' works at the end of a file
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file_end.txt')
    data = [
        'file_end line 1', 'file_end line 2', 'file_end line 3',
        'file1 line 1', 'file1 line 2', 'file1 line 3', 'file1 line 4'
    ]

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_lines():
    """Testing the line count for each line, with an included file

    Note that the line count includes the line with 'include'
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file_middle.txt')

    num = [1, 2, 1, 2, 3, 4, 4]
    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert fd.lineno == num[i]
            i += 1


def test_total_lines():
    """Testing the total number of lines with an included file

    Note that the line count includes the line with 'include'
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file_middle.txt')

    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            pass
        assert fd.total_lines == 8


def test_nested_includes():
    """Testing an include within an include
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file_include1.txt')
    data = [
        'file_include1 line1', 'file_end line 1', 'file_end line 2',
        'file_end line 3', 'file1 line 1', 'file1 line 2', 'file1 line 3',
        'file1 line 4'
    ]

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_include_empty_file():
    """Testing that including an empty file works
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'include_empty_file.txt')
    data = ['file_end line 1', 'file_end line 2', 'file_end line 3']

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_blank_lines():
    """Testing that empty lines and ones with just blanks don't
    cause any problems
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'include_blank_lines.txt')
    data = [
        'file_end line 1', '', 'file_end line 3', 'blank_lines first line',
        '   ', '', 'blank_lines 4th line', '   ', ''
    ]

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert line[0:-1] == data[i]
            i += 1


def test_stack():
    """Testing the stack of files part way through reading includes
    """
    cwd = os.path.dirname(__file__)
    datapath = os.path.join(cwd, 'data')
    filepath = os.path.join(datapath, 'file_include1.txt')
    data = ['data/file1.txt:2', 'data/file_end.txt:4']

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            i += 1
            if i == 6:
                stack = []
                for line in fd.stack():
                    stack.append(os.path.relpath(line, cwd))
                assert stack == data
                break


def test_different_include():
    """Testing that '#include' works
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file_#include.txt')
    data = [
        'file_middle line 1', 'file_middle line 2', 'file1 line 1',
        'file1 line 2', 'file1 line 3', 'file1 line 4', 'file_middle line 3'
    ]

    i = 0
    with seamm_util.Open(filepath, 'r', include='#include') as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1


def test_push():
    """Testing that the default 'include' works
    """
    datapath = os.path.join(os.path.dirname(__file__), 'data')
    filepath = os.path.join(datapath, 'file_middle.txt')
    data = [
        'file_middle line 1', 'file_middle line 2', 'file1 line 1',
        'file1 line 2', 'file1 line 3', 'file1 line 4', 'file_middle line 3',
        'file1 line 4', 'file_middle line 3'
    ]

    i = 0
    with seamm_util.Open(filepath, 'r', include='include') as fd:
        for line in fd:
            assert line.strip() == data[i]
            i += 1
            if i == 7:
                fd.push(2)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_util` package, Dictionary module."""

from seamm_util import Dictionary
import sys


def test_create():
    """Testing that we can create a Dictionary object."""
    d = Dictionary()
    assert str(type(d)) == "<class 'seamm_util.dictionary.Dictionary'>"


def test_set_get_item():
    """Testing setting and then getting an item."""
    d = Dictionary()
    d['a'] = 53
    assert d['a'] == 53


def test_len():
    """Testing getting the length of a dictionary."""
    d = Dictionary()
    d['a'] = 53
    assert len(d) == 1


def test_del_item():
    """Testing that we can delete an item."""
    d = Dictionary()
    d['a'] = 53
    del d['a']
    assert len(d) == 0


def test_iter():
    """Testing that we can iterate over a Dictionary."""
    d = Dictionary(ordered=True)
    d.update({'a': 1, 'b': 2, 'c': 3})
    keys = []
    for key in d:
        keys.append(key)

    assert keys == ['a', 'b', 'c']


def test_str():
    """Testing that we can get a str representation."""
    d = Dictionary(ordered=True)
    d.update(a=1, b=2, c=3)
    if sys.version_info >= (3, 7):
        assert str(d) == "{'a': 1, 'b': 2, 'c': 3}"
    else:
        assert str(d) == "OrderedDict([('a', 1), ('b', 2), ('c', 3)])"


def test_repr():
    """Testing that we can get an official representation."""
    d = Dictionary(ordered=True)
    d.update(a=1, b=2, c=3)
    if sys.version_info >= (3, 7):
        assert repr(d) == "{'a': 1, 'b': 2, 'c': 3}"
    else:
        assert repr(d) == "OrderedDict([('a', 1), ('b', 2), ('c', 3)])"


def test_fromkeys():
    """Test the class method fromkeys."""
    d = Dictionary.fromkeys(['a', 'b', 'c'], 1)
    assert repr(d) == "{'a': 1, 'b': 1, 'c': 1}"


def test_copy():
    """Testing that we can get an official representation."""
    d = Dictionary(ordered=True)
    d.update(a=1, b=2, c=3)

    e = d.copy()
    d['b'] = 10

    if sys.version_info >= (3, 7):
        assert repr(e) == "{'a': 1, 'b': 10, 'c': 3}"
    else:
        assert repr(e) == "OrderedDict([('a', 1), ('b', 10), ('c', 3)])"

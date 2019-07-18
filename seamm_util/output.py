# -*- coding: utf-8 -*-

"""A class for wrapping output from the MolSSI Framework and plugins.
Initially it is a thin wrapper around a dictionary to store the output,
using JSON to serialize and deserialize the data.

It presents the dict api with the addition of methods to serialize and
deserialize the contents.
"""

import bz2
import collections.abc
import gzip
import json
import os.path
import pprint


class Output(collections.abc.MutableMapping):

    def __init__(self, filename=None, **kwargs):
        """Create the Output object

        Keyword arguments:
            filename: the name of the file for serialization
            kwargs: any other keyword arguments initialize the dict
        """

        self._is_changed = False
        self._data = dict()  # This stores the dict like data
        self._filename = None

        # Set the filename, if given, which will open the file
        self.filename = filename

        # Finally, process any extra keywords
        if len(kwargs) > 0:
            self.update(dict(**kwargs))

    @property
    def filename(self):
        """The filename for the serialized data"""
        return self._filename

    @filename.setter
    def filename(self, filename):
        if filename != self._filename:
            if self._filename is None:
                if self._is_changed:
                    pass
            else:
                if self._is_changed:
                    self.flush()
            self._filename = filename

        if self._filename is not None:
            with self._open() as fd:
                self._data = json.load(fd)
            self._is_changed = False

    def __getitem__(self, key):
        """Allow [] access to the dictionary!"""
        if key not in self._data:
            raise KeyError("key '" + key + "' does not exist")
        return self.get(key)

    def __setitem__(self, key, value):
        """Allow x[key] access to the data"""
        self._data[key] = value
        self._is_changed = True

    def __delitem__(self, key):
        """Allow deletion of keys"""
        del self._data[key]
        self._is_changed = True

    def __iter__(self):
        """Allow iteration over the object"""
        return iter(self._data)

    def __len__(self):
        """The len() command"""
        return len(self._data)

    def __repr__(self):
        """The string representation of this object"""
        return repr(self._data)

    def __str__(self):
        """The pretty string representation of this object"""
        return pprint.pformat(self._data)

    def copy(self):
        """Return a shallow copy of the dictionary"""
        return self._data.copy()

    def _open(self):
        """Open self.filename, using compression according to its extension,
        """

        extension = os.path.splitext(self.filename)[1].strip().lower()
        if extension == '.bz2':
            fd = bz2.open(self.filename, 'rt')
        elif extension == '.gz':
            fd = gzip.open(self.filename, 'rt')
        else:
            fd = open(self.filename, 'r')

        return fd

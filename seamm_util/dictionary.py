# -*- coding: utf-8 -*-

"""
Provides a Dictionary, identical to a dict, but which can be subclassed safely.
"""

import collections
import collections.abc
import copy
import sys


class Dictionary(collections.abc.MutableMapping):
    """Class that acts like a dictionary, but can safely be subclassed.

    The Dictionary class implements a dictionary-like class that other
    classes can inherit from. In addition, __init__ accepts a keyword
    'ordered' specifying the use of an ordered dictionary.
    """

    @classmethod
    def fromkeys(cls, iterable, value=None):
        """Create a new Dictionary with keys from iterable and values set to
        value.
        """
        result = cls()
        result.data = dict.fromkeys(iterable, value)
        return result

    def __init__(self, *args, ordered=False, **kwargs):
        """Initialize a Dictionary, optionally with data.

        Parameters
        ----------
        args : dict
            0+ dictionaries to update from, in order

        ordered : bool, optional
            A Boolean indicating whether to use an ordered dictionary.

        kwargs : keyword - value pairs
            0+ named arguments to update from
        """
        if ordered:
            # Before python 3.7 dictionaries were not ordered.
            if sys.version_info >= (3, 7):
                self.data = dict()
            else:
                self.data = collections.OrderedDict()
        else:
            self.data = dict()

        self.update(*args, **kwargs)

    # Provide dict like access to the data

    def __getitem__(self, key):
        """Allow [] access to the data."""
        return self.data[key]

    def __setitem__(self, key, value):
        """Allow x[key] access to the data."""
        self.data[key] = value

    def __delitem__(self, key):
        """Allow deletion of keys."""
        del self.data[key]

    def __iter__(self):
        """Allow iteration over the object."""
        return iter(self.data)

    def __len__(self):
        """The len() command."""
        return len(self.data)

    def __str__(self):
        """Printable string representation."""
        return str(self.data)

    def __repr__(self):
        """Official string representation."""
        return repr(self.data)

    def copy(self):
        """Return a shallow copy."""
        return copy.copy(self)

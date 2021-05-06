# -*- coding: utf-8 -*-

"""Utility routines to help with variable names for scripts"""

from keyword import iskeyword
import re


def is_valid(name):
    """Check if a variable name is valid and is not a keyword"""
    return name.isidentifier() and not iskeyword(name)


def clean(raw_name):
    """Fix up an input string so that it is a valid variable name"""

    # Remove invalid characters
    name = re.sub("[^0-9a-zA-Z_]", "_", raw_name)

    # Check that it is a valid variable name. If not
    # put an underscore on the front

    if not is_valid(name):
        name = "_" + name

    # should be valid, but check once more
    if not is_valid(name):
        raise RuntimeError(
            "Variable name {} (from {}) is not valid!".format(name, raw_name)
        )

    return name

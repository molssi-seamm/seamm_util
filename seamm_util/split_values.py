# -*- coding: utf-8 -*-

"""Split a string of values typed by a user, such as several SMILES."""

import shlex


def split_values(text):
    """The values in ``text``: separated by whitespace, with single or double quotes
    around a value that contains spaces.

    A backslash is kept as it is, since it is part of values such as SMILES
    (``C/C=C\\C``, a Z double bond). ``shlex.split`` treats it as an escape and
    drops it, which silently turns a Z isomer into an unspecified or E one. '#' (a
    triple bond in SMILES) does not start a comment.

    Parameters
    ----------
    text : str
        The values, e.g. ``"CCO 'C/C=C\\C' C#N"``.

    Returns
    -------
    [str]
        The values, e.g. ``["CCO", "C/C=C\\C", "C#N"]``.
    """
    lexer = shlex.shlex(str(text), posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    lexer.escape = ""
    return list(lexer)

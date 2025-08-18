# -*- coding: utf-8 -*-

"""Tools for handling the shorthand definitions of lists in SEAMM."""


def parse_list(input, duplicates=True, sort=False, **kwargs):
    """Parse a SEAMM-style list of values, including ranges.

    Parameters
    ----------
    input : str
        The list definition (see below).
    duplicates : bool = True
        Allows duplicate values in the list by default.
    sort : bool = False
        If False, the list is not sorted. True or "ascending" sorts into ascending order
        while "descending" into reverse order. Only the first letter is tested, so any
        abbreviation works.
    kwargs : {str: any}
        Optional dictionary of values of variables used in the list.

    Returns
    -------
    list : [int or float]
        The expanded list of values

    The input list definition consists of any number of individual values or ranges,
    separated by commas (','). Ranges are similar to those in Python *except* that the
    'stop' value is included in the list if stop = start + n*step. Ranges are defined as
    start:stop[:step]. If step is ommitted, it defaults to 1.

    Examples
    --------
    A simple, commma delimited list is transformed into a python list:

    >>> parse_list("1, 2, 4, 5")
    [1, 2, 4, 5]

    If any of the values is a float, the result is also a float

    >>> parse_list("1, 2.0, 4, 5")
    [1, 2.0, 4, 5]

    This is a simple range:

    >>> parse_list("1:6")
    [1, 2, 3, 4, 5, 6]

    Note that the stop value is include in the result. This is different than a python
    range where the termination is <, not <=. This is more natural for users of SEAMM.
    For example, scanning a dihedral angle from 0 to 180 degrees, most people will
    expect 180 to be in the list.

    Now using a step of 2:

    >>> parse_list("1:6:2")
    [1, 3, 5]

    Note that the stop value is not included in the output in this case.

    The step can be negative as long as stop < start:

    >>> parse_list("6:1:-2")
    [6, 4, 2]

    Now we can put it all together:

    >>> parse_list("1, 2.0, 4, 5, 1:6, 1:6:2")
    [1, 2.0, 4, 5, 1, 2, 3, 4, 5, 6, 1, 3, 5]

    Note that a value can appear multiple times in a simple list. This can be controlled
    by setting duplicates = False:

    >>> parse_list("1, 2.0, 4, 5, 1:6, 1:6:2", duplicates=False)
    [1, 2.0, 4, 5, 3, 6]

    You can also sort the results into ascending or descending order:

    >>> parse_list("1, 2.0, 4, 5, 1:6, 1:6:2", sort="ascending")
    [1, 1, 1, 2.0, 2, 3, 3, 4, 4, 5, 5, 5, 6]

    and if you want to remove the duplicates too:

    >>> parse_list("1, 2.0, 4, 5, 1:6, 1:6:2", duplicates=False, sort="descending")
    [6, 5, 4, 3, 2.0, 1]

    Where do variable fit? Any of the values in the input string can be variables as
    as long as values are are given as keyword arguments:

    >>> parse_list("first:last:incr", first=1, last=6, incr=0.5)
    [1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]

    It is often convenient if the variables are in a dictionary:

    >>> values = {"first": 6, "last": 1, "incr":-0.5}
    >>> parse_list("first:last:incr", **values)
    [6, 5.5, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5]
    """
    _globals = {
        "__builtins__": None,
    }
    result = []
    for part in input.split(","):
        if ":" in part:
            # A range...
            tmp = part.split(":")
            if len(tmp) == 3:
                start, stop, step = tmp
            elif len(tmp) == 2:
                start, stop = tmp
                step = "1"
            else:
                raise RuntimeError(f"Badly formed range '{part}' in parse_list")

            start = eval(start, _globals, kwargs)
            stop = eval(stop, _globals, kwargs)
            step = eval(step, _globals, kwargs)

            # Sanity checks!
            if step == 0:
                raise ValueError("A step of zero is not allow in ranges!")
            elif step < 0 and start < stop:
                raise ValueError(f"If start < stop, the step must be positive: {step}")
            elif step > 0 and start > stop:
                raise ValueError(f"If stop < start, the step must be negative: {step}")

            # Flip the sign of the test if counting down
            sign = -1 if step < 0 else 1
            value = start

            # Add a very small number for roundoff in floats
            while sign * (stop - value + stop / 1.0e8) >= 0:
                if not duplicates:
                    for tmp in result:
                        if abs(value - tmp) < 1.0e-8:
                            break
                    else:
                        result.append(value)
                else:
                    result.append(value)
                value += step
        else:
            value = eval(part, _globals, kwargs)
            result.append(value)

    if isinstance(sort, str):
        if sort[0] == "d":
            result.sort(reverse=True)
        elif sort[0] == "a":
            result.sort()
        else:
            raise ValueError("'sort' must be 'a...' or 'd...' or a bool")
    elif sort:
        result.sort()

    return result


if __name__ == "__main__":
    import doctest

    result = doctest.testmod(verbose=False)

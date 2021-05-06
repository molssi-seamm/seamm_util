# -*- coding: utf-8 -*-

"""Functions for handling executables"""

import logging
import os
import os.path

logger = logging.getLogger(__name__)


def check_executable(executable):
    """Check that an executable exists.

    Check that an executable exists and is executable. If no path is
    given, but just the executable name, then the current path is
    checked.  If the executable is missing or not actually executable
    this function raises a useful error with a message letting the
    user know where the path came from -- a command line option, an
    environment variable, configuration file, or default.

    Parameters:
        executable -- required positional parameter giving the name of
            the executable as a string. It can be a simple name or contain
            a path to the executable.

    Returns:
        The string for the path to the executable. If it was found on the path,
        the full path is returned, otherwise the return is the same as the
        executable string passed in.

    Errors:
        FileNotFoundError if the executable is not found or is not executable.
            The message contains information about where the option came from,
            either the command-line, an environment variable, configuration
            file or the default.
    """

    if os.path.dirname(executable) == "":
        # A simple name without a directory part was given, so see if the
        # executable exists in the path.
        path = os.get_exec_path()
        exes = []
        for dir in path:
            exe = os.path.join(dir, executable)
            if os.path.isfile(exe):
                if os.access(exe, os.X_OK):
                    return exe
                else:
                    exes.append(exe)
        msg = "The executable '{}' was not found in the path:\n\t".format(executable)
        msg += "\n\t".join(path)
        msg += "\n"
        if len(exes) > 0:
            msg += (
                "However, the following files were found, but were not "
                "executable:\n\t"
            )
            msg += "\n\t".join(exes)
            msg += "\n"
    else:
        #  A path before the executable name was given, so try as is
        if os.path.isfile(executable):
            if os.access(executable, os.X_OK):
                return executable
            else:
                msg = "The executable '{}' exists, but is not executable!\n".format(
                    executable
                )
        else:
            msg = "The executable '{}' does not exist!\n".format(executable)

    raise FileNotFoundError(msg)

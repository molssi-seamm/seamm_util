# -*- coding: utf-8 -*-

"""Functions for handling executables"""

import logging
import os
import os.path

logger = logging.getLogger(__name__)

# from configargparse.py
_COMMAND_LINE_SOURCE_KEY = "command_line"
_ENV_VAR_SOURCE_KEY = "environment_variables"
_CONFIG_FILE_SOURCE_KEY = "config_file"
_DEFAULTS_SOURCE_KEY = "defaults"


def check_executable(executable, key=None, parser=None):
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

        key -- string giving the command-line option used in
            generating the path. These normally start with two dashes,
            e.g. --openbabel-path. (optional)

        parser -- the ConfigArgParser used to parse the options. (optional)

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

    if os.path.dirname(executable) == '':
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
        msg = (
            "The executable '{}' was not found in the path:\n\t"
            .format(executable)
        )
        msg += '\n\t'.join(path)
        msg += '\n'
        if len(exes) > 0:
            msg += (
                'However, the following files were found, but were not '
                'executable:\n\t'
            )
            msg += '\n\t'.join(exes)
            msg += '\n'
    else:
        #  A path before the executable name was given, so try as is
        if os.path.isfile(executable):
            if os.access(executable, os.X_OK):
                return executable
            else:
                msg = (
                    "The executable '{}' exists, but is not executable!\n"
                    .format(executable)
                )
        else:
            msg = "The executable '{}' does not exist!\n".format(executable)

    if key is not None and parser is not None:
        source_key_to_display_value_map = {
            _COMMAND_LINE_SOURCE_KEY: "Command Line Args: ",
            _ENV_VAR_SOURCE_KEY: "Environment Variables:\n",
            _CONFIG_FILE_SOURCE_KEY: "Config File (%s):\n",
            _DEFAULTS_SOURCE_KEY: "Defaults:\n"
        }
        for source, settings in parser._source_to_settings.items():
            source = source.split("|")
            if source[0] == _COMMAND_LINE_SOURCE_KEY:
                junk, values = settings['']
                if key in values:
                    msg += (
                        "The path came from the key '{}', which was "
                        'set on the command-line.'
                    ).format(key)
                    break
            elif source[0] == _ENV_VAR_SOURCE_KEY:
                env_var = parser._option_string_actions[key].env_var
                if env_var:
                    if env_var in settings:
                        msg += (
                            "The path came from the environment variable "
                            "'{}', whose value is '{}'"
                        ).format(env_var, settings[env_var][1])
                        break
            elif source[0] == _CONFIG_FILE_SOURCE_KEY:
                for tmp_key, (action, value) in settings.items():
                    if action:
                        if key in action.option_strings:
                            msg += (
                                "The path came from the configuration "
                                "file '{}', key '{}', whose value is '{}'"
                            ).format(source[1], key, value)
                            break
            elif source[0] == _DEFAULTS_SOURCE_KEY:
                for tmp_key, (action, value) in settings.items():
                    if action:
                        if key in action.option_strings:
                            msg += (
                                "The path came from the default "
                                "for the option '{}', which is '{}'"
                            ).format(key, value)
                            break
            else:
                # Shouln't get here, but if we do, just print what we know.
                source = (
                    source_key_to_display_value_map[source[0]] %
                    tuple(source[1:])
                )
                print(source)
                for tkey, (action, value) in settings.items():
                    if tkey:
                        print("  %-19s%s\n" % (tkey + ":", value))
                    else:
                        if isinstance(value, str):
                            print("  %s\n" % value)
                        elif isinstance(value, list):
                            print("  %s\n" % ' '.join(value))

    raise FileNotFoundError(msg)

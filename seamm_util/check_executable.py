# -*- coding: utf-8 -*-

"""Functions for handling executables"""

import configargparse
import logging
import os
import os.path
import pprint
import seamm_util

logger = logging.getLogger(__name__)


# from configargparse.py
_COMMAND_LINE_SOURCE_KEY = "command_line"
_ENV_VAR_SOURCE_KEY = "environment_variables"
_CONFIG_FILE_SOURCE_KEY = "config_file"
_DEFAULTS_SOURCE_KEY = "defaults"


def check_executable(executable, key=None, parser=None):
    """Check that an executable exists.

    Check that an executable exists and is the path if a full path is
    not given. Raise a useful error message if it doesn't exist,
    giving where the path came from, etc.
    """

    if os.path.dirname(executable) == '':
        # see if the executable exists in the path
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
                    source = (
                        source_key_to_display_value_map[source[0]]
                        % tuple(source[1:])
                    )
                    print(source)
                    for tkey, (action, value) in settings.items():
                        if tkey:
                            print("  %-19s%s\n" % (tkey+":", value))
                        else:
                            if isinstance(value, str):
                                print("  %s\n" % value)
                            elif isinstance(value, list):
                                print("  %s\n" % ' '.join(value))
    else:
        # have a path before the executable name, so try as is
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
                    source = (
                        source_key_to_display_value_map[source[0]]
                        % tuple(source[1:])
                    )
                    print(source)
                    for tkey, (action, value) in settings.items():
                        if tkey:
                            print("  %-19s%s\n" % (tkey+":", value))
                        else:
                            if isinstance(value, str):
                                print("  %s\n" % value)
                            elif isinstance(value, list):
                                print("  %s\n" % ' '.join(value))
    
    raise FileNotFoundError(msg)

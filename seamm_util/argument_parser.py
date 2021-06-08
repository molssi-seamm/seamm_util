# -*- coding: utf-8 -*-

"""A configuration and argument parser tailored to SEAMM.

The goal of this is to allow options to be specified both on the
command line and in ini files, with command line having
precedence. This is tailored to SEAMM flowcharts so that options for
each type of step (plug-in) is in its own section on the command line
or in the ini file, labeled by the type of section.
"""

import argparse
import configparser
import logging
import os
import sys

# logging.basicConfig(level="WARNING")
logger = logging.getLogger(__name__)

# Used in parser getters to indicate the default behaviour when a specific
# option is not found it to raise an exception. Created to enable `None' as
# a valid fallback value.
_UNSET = object()


class ArgumentParser(object):
    """Replacement and extension for argparse.ArgumentParser that adds
    support for .ini files plus something like the subcommands in
    argparse but with multiple ones active at the same time.

    This is accomplished by separating sections with
    '<section name>' on the commandline, and using
    '[<section name>] in the .ini files. e.g.

    test.flow lammps-step --log-level debug psi4-step --np 32
    """

    def __init__(
        self,
        *args,
        ini_files=[
            "etc/SEAMM/seamm.ini",
            os.path.expanduser("~/SEAMM/seamm.ini"),
            "seamm.ini",
        ],
        interpolation=configparser.ExtendedInterpolation(),
        **kwargs,
    ):
        """Command-line and .ini parser for SEAMM"""

        self._parsers = {}
        self._ini_files = ini_files
        self._interpolation = interpolation
        if self._interpolation is None:
            self._interpolation = configparser.Interpolation()
        self._options = {}
        self._origins = {}
        self._ini_files_used = []

    def add_parser(
        self,
        section,
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        parents=[],
        formatter_class=argparse.HelpFormatter,
        prefix_chars="-",
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler="error",
        add_help=True,
        allow_abbrev=True,
    ):
        """Capture the information needed to create a subparser.

        Parameters
        ----------
        section : str
            The name of this section of the parsing.
        prog : str = sys.argv[0]
            The name of the program
        usage : str = None
            A usage message (default: auto-generated from arguments)
        description : str = None
            A description of what the program does
        epilog : str = None
            Text following the argument descriptions
        parents : [argparse.ArgumentParser] = []
            Parsers whose arguments should be copied into this one
        formatter_class : argparse.HelpFormatter
            HelpFormatter class for printing help messages
        prefix_chars : str = '-'
            Characters that prefix optional arguments
        fromfile_prefix_chars : str = None
            Characters that prefix files containing additional arguments
        argument_default : str = None
            The default value for all arguments
        conflict_handler : str = 'error'
            String indicating how to handle conflicts
        add_help : bool = True
            Add a -h/-help option
        allow_abbrev : bool = True
            Allow long options to be abbreviated unambiguously
        """
        if section in self._parsers:
            raise ValueError(f"Parser '{section}' already exists")
        data = self._parsers[section] = {"arguments": [], "groups": {}}
        data["init_args"] = {
            "prog": prog,
            "usage": usage,
            "description": description,
            "epilog": epilog,
            "parents": parents,
            "formatter_class": formatter_class,
            "prefix_chars": prefix_chars,
            "fromfile_prefix_chars": fromfile_prefix_chars,
            "argument_default": argument_default,
            "conflict_handler": conflict_handler,
            "add_help": add_help,
            "allow_abbrev": allow_abbrev,
        }

    def exists(self, name):
        return name in self._parsers

    def add_argument(self, section, *args, **kwargs):
        if section not in self._parsers:
            raise KeyError(f"Parser '{section}' does not exist.")
        self._parsers[section]["arguments"].append((args, kwargs))

    def add_argument_group(self, section, title, description=None):
        if section not in self._parsers:
            raise KeyError(f"Parser '{section}' does not exist.")
        self._parsers[section]["groups"][title] = {"description": description}

    def parse_args(self, args=None):
        """Parse the .ini file and command-line arguments.

        There are three distinct steps to the process:

            1. Process the command-line arguments, breaking them into
               sections corresponding to the subparsers.
            2. Read the .ini files, if any.
            3. Create the actual parsers from the saved information,
               replacing or adding defaults for any values found in the
               .ini files.
            4. Parse each section of the command-line with the correct parser.

        Parameters
        ----------
        args : [str] = sys.argv[1:]
            The arguments to parse. Defaults to the command-line arguments.
        """
        if args is None:
            args = sys.argv[1:]

        # Check for help!
        if "-h" in args or "--help" in args:
            self.print_help(args)
            exit()

        # 1. Process the command-line arguments, breaking them into
        #    sections corresponding to the subparsers.

        arg_sections = self.split_args(args)

        # 2. Read the .ini files, if any.

        config = configparser.ConfigParser(interpolation=None)
        self._ini_files_used = config.read(self._ini_files)

        # 3. Create the actual parsers from the saved information,
        #    replacing or adding defaults for any values found in the
        #    .ini files.

        self._options = {}
        self._origins = {}
        defaults = {}
        groups = {}
        for section, data in self._parsers.items():
            # The parser
            parser = argparse.ArgumentParser(**data["init_args"])

            # Any groups
            for group, kwargs in data["groups"].items():
                groups[group] = parser.add_argument_group(group, **kwargs)

            # Need to add or replace default if the variable was in a .ini
            # file. This next code is straight for argparse to make sure we
            # have the variable's name in 'dest'.
            for args, kwargs in data["arguments"]:
                if not args or len(args) == 1 and args[0][0] not in parser.prefix_chars:
                    variable = args[0]
                else:
                    kwargs = parser._get_optional_kwargs(*args, **kwargs)
                    variable = kwargs["dest"]
                    args = kwargs["option_strings"]
                    del kwargs["option_strings"]
                # See if it was in the .ini files
                try:
                    tmp = variable.replace("_", "-")
                    if config.has_section(section):
                        default = config.get(section, tmp)
                    else:
                        default = config.get(configparser.DEFAULTSECT, tmp)
                    kwargs["default"] = default
                    # Track what the default is and where it comes from
                    defaults[variable] = {"origin": "configfile"}
                    # May need to convert the type of the default
                    if "type" in kwargs:
                        default = kwargs["type"](default)
                    kwargs["default"] = default
                except Exception:
                    # Track what the default is and where it comes from
                    defaults[variable] = {"origin": "default"}

                # and finally add the argument to the parser.
                group = kwargs.pop("group", None)
                if group is not None:
                    if group not in groups:
                        raise ValueError(f"argument group '{group}' is not defined")
                    groups[group].add_argument(*args, **kwargs)
                else:
                    parser.add_argument(*args, **kwargs)

                defaults[variable]["value"] = parser.get_default(variable)

            # 4. Parse each section of the command-line with the correct parser
            tmp = parser.parse_args(arg_sections[section])
            self._options[section] = vars(tmp)

            origin = self._origins[section] = {}
            for variable, value in self._options[section].items():
                if variable in defaults:
                    if value == defaults[variable]["value"]:
                        origin[variable] = defaults[variable]["origin"]
                    else:
                        origin[variable] = "commandline"
                else:
                    origin[variable] = "commandline"

        # Handle any interpolations, putting the results in a temporary mirror
        tmp = {}
        for section, options in self._options.items():
            data = tmp[section] = {}
            for option, value in options.items():
                if isinstance(value, str):
                    value = self._interpolation.before_get(
                        self, section, option, value, options
                    )
                data[option] = value

        # Override the options with the mirror.
        self._options = tmp

        return self._options

    def get(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        """Get an option value for a given section.

        If `vars' is provided, it must be a dictionary. The option is looked up
        in `vars' (if provided), `section', and in `DEFAULTSECT' in that order.
        If the key is not found and `fallback' is provided, it is used as
        a fallback value. `None' can be provided as a `fallback' value.

        If interpolation is enabled and the optional argument `raw' is False,
        all interpolations are expanded in the return values.

        Arguments `raw', `vars', and `fallback' are keyword only.

        The section DEFAULT is special.
        """
        try:
            d = self._options[section]
        except KeyError:
            if fallback is _UNSET:
                raise
            else:
                return fallback
        option = self.optionxform(option)
        try:
            value = d[option]
        except KeyError:
            if fallback is _UNSET:
                raise configparser.NoOptionError(option, section)
            else:
                return fallback

        if raw or value is None:
            return value
        else:
            return self._interpolation.before_get(self, section, option, value, d)

    def get_options(self, section=None):
        """Return the options for the given section.

        Parameters
        ----------
        section : str = None
            Return the options for the given section, or all sections

        Returns
        -------
        {str: int, float, str or bool}
            The dictionary of options for the section, or all sections.
        """
        if section is None:
            return {**self._options}
        else:
            return {**self._options[section]}

    def get_origins(self, section=None):
        """Return the origins of the options for the given section.

        Parameters
        ----------
        section : str = None
            Return the origins for the given section, or all sections

        Returns
        -------
        {str: str}
            The dictionary of origins for the section, or all sections.
        """
        if section is None:
            return {**self._origins}
        else:
            return {**self._origins[section]}

    def get_ini_files(self):
        """Return a list of the .ini files actually used.

        Returns
        -------
        [str] :
            The list of .ini files found
        """
        return [*self._ini_files_used]

    def optionxform(self, optionstr):
        return optionstr.lower()

    def print_help(self, args=None, fd=sys.stdout):
        fd.write(self.format_help(args))

    def format_help(self, args=None):
        """Prepare the help message.

        Parameters
        ----------
        args : [str] = sys.argv[1:]
            The arguments to pass the parsers, defaults to sys.argv[1:]
        """
        if args is None:
            args = sys.argv[1:]

        # 1. Process the command-line arguments, breaking them into
        #    sections corresponding to the subparsers.

        # parser = argparse.ArgumentParser(prefix_chars='+')
        # parser.add_argument('SEAMM', nargs='*', default='')
        # for section in self._parsers:
        #     parser.add_argument(f'++{section}', nargs='*', default='')
        # arg_sections = vars(parser.parse_args(args))
        # del parser

        arg_sections = self.split_args(args)

        # What to do depends on where the --help (or -h) flag is. If it is in
        # the SEAMM section, print its help plus the plug-ins. Otherwise,
        # print the help for that plug-in.

        section_args = arg_sections["SEAMM"]
        if "--help" in section_args or "-h" in section_args:
            # set up any SEAMM options
            groups = {}
            if "SEAMM" in self._parsers:
                data = self._parsers["SEAMM"]

                # The parser
                parser = argparse.ArgumentParser(**data["init_args"])

                # Any groups
                for group, kwargs in data["groups"].items():
                    groups[group] = parser.add_argument_group(group, **kwargs)

                # and the arguments
                for args, kwargs in data["arguments"]:
                    group = kwargs.pop("group", None)
                    if group is not None:
                        if group not in groups:
                            raise ValueError(f"argument group '{group}' is not defined")
                        groups[group].add_argument(*args, **kwargs)
                    else:
                        parser.add_argument(*args, **kwargs)
            else:
                parser = argparse.ArgumentParser()

            # and then the plug-ins
            plugins = parser.add_argument_group(
                "plug-ins",
                description=(
                    "The plug-ins in this flowchart, which have their own " "options."
                ),
            )
            for section, data in self._parsers.items():
                if section == "SEAMM":
                    continue
                init_args = data["init_args"]
                if "description" in init_args:
                    plugins.add_argument(section, help=init_args["description"])
                else:
                    plugins.add_argument(section)
            return parser.format_help()

        # Find the first section what contains '--help', and return its help.
        groups = {}
        for section, data in self._parsers.items():
            section_args = arg_sections[section]
            if "--help" in section_args or "-h" in section_args:
                # The parser
                parser = argparse.ArgumentParser(**data["init_args"])

                # Any groups
                for group, kwargs in data["groups"].items():
                    groups[group] = parser.add_argument_group(group, **kwargs)

                for args, kwargs in data["arguments"]:
                    group = kwargs.pop("group", None)
                    if group is not None:
                        if group not in groups:
                            raise ValueError(f"argument group '{group}' is not defined")
                        groups[group].add_argument(*args, **kwargs)
                    else:
                        parser.add_argument(*args, **kwargs)
                return parser.format_help()

    def items(self, section=_UNSET, raw=False, vars=None):
        """Return a list of (name, value) tuples for each option in a section.

        All % interpolations are expanded in the return values, based on the
        defaults passed into the constructor, unless the optional argument
        `raw' is true.  Additional substitutions may be provided using the
        `vars' argument, which must be a dictionary whose contents overrides
        any pre-existing defaults.

        The section DEFAULT is special.
        """
        if section is _UNSET:
            return super().items()
        try:
            d = self._options[section]
        except KeyError:
            if section != self.default_section:
                raise configparser.NoSectionError(section)
        orig_keys = list(d.keys())
        # Update with the entry specific variables
        if vars:
            for key, value in vars.items():
                d[self.optionxform(key)] = value
        if raw:

            def value_getter(option):
                return d[option]

        else:

            def value_getter(option):
                return self._interpolation.before_get(
                    self, section, option, d[option], d
                )

        return [(option, value_getter(option)) for option in orig_keys]

    def split_args(self, args=None):
        """Break the argument line into sections for each plug-in.

        Parameters
        ----------
        args : [str] = sys.argv[1:]

        Returns
        -------
        dict[str: [str]]
            A dictionary with entries of an array of strings for all plug-ins
            plus 'SEAMM'
        """
        sections = self._parsers.keys()
        result = {x: [] for x in sections}
        result["SEAMM"] = []

        section = "SEAMM"
        for arg in args:
            if arg in sections:
                section = arg
            else:
                result[section].append(arg)

        return result


#
# Keep a list of named parsers and a method to create/return one of them
#
_parsers = {}


def getParser(name="SEAMM", **kwargs):
    """Get the named command-line argument parser.

    Returns
    -------
    ArgumentParser
        The seamm.ArgumentParser for handling commandline and
        config-file parsing.
    """

    global _parsers
    if name not in _parsers:
        logger.info(f"Creating parser '{name}'.")
        _parsers[name] = ArgumentParser(**kwargs)

    logger.info(f"Returning parser '{name}' ({_parsers[name]})")
    return _parsers[name]


def seamm_parser(name="SEAMM"):
    """Setup the command-line argument parser for SEAMM.

    Returns
    -------
    ArgumentParser
        The seamm.ArgumentParser for handling commandline and
        config-file parsing.
    """
    parser = getParser(name=name)

    if parser.exists("SEAMM"):
        return parser

    parser.add_parser(
        "SEAMM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog=sys.argv[0],
    )

    # Main options
    parser.add_argument_group(
        "SEAMM",
        "main options",
        "The main options for SEAMM",
    )

    parser.add_argument(
        "SEAMM",
        "--root",
        group="main options",
        dest="root",
        default="~/SEAMM",
        action="store",
        help="The root directory for SEAMM data, default: %(default)s",
    )
    parser.add_argument(
        "SEAMM",
        "--datastore",
        group="main options",
        dest="datastore",
        default="${root}/Jobs",
        action="store",
        help="The datastore (directory) for this run, default: %(default)s",
    )
    parser.add_argument(
        "SEAMM",
        "--job-id-file",
        group="main options",
        dest="job_id_file",
        default=None,
        action="store",
        help="The job_id file to use.",
    )
    parser.add_argument(
        "SEAMM",
        "--dashboards",
        group="main options",
        dest="dashboards",
        default="${root}/dashboards.ini",
        action="store",
        help="The configuration file for accessible dashboards: %(default)s",
    )

    # Debugging options
    parser.add_argument_group(
        "SEAMM",
        "debugging options",
        "Options for turning on debugging output and tools",
    )

    parser.add_argument(
        "SEAMM",
        "--log-level",
        group="debugging options",
        default="WARNING",
        type=str.upper,
        choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="The level of informational output, default: '%(default)s'",
    )

    # add options for the job
    parser.add_argument_group("SEAMM", "job options", "Options for jobs")

    parser.add_argument(
        "SEAMM",
        "--standalone",
        group="job options",
        action="store_true",
        help="Run this workflow as-is without using the job, etc.",
    )
    parser.add_argument(
        "SEAMM",
        "--project",
        group="job options",
        dest="projects",
        action="append",
        help="The project(s) for this job.",
    )
    parser.add_argument(
        "SEAMM",
        "--title",
        group="job options",
        dest="title",
        default="",
        action="store",
        help="The title for this run.",
    )
    parser.add_argument(
        "SEAMM",
        "--force",
        group="job options",
        dest="force",
        action="store_true",
        help="Overwrite the job output if it exists.",
    )

    # Hardware options
    parser.add_argument_group(
        "SEAMM",
        "hardware options",
        (
            "Options about memory limits, parallelism and other details "
            "connected with hardware."
        ),
    )

    parser.add_argument(
        "SEAMM",
        "--parallelism",
        group="hardware options",
        default="any",
        choices=["none", "mpi", "openmp", "any"],
        help="Whether to limit parallel usage to certain types.",
    )

    parser.add_argument(
        "SEAMM",
        "--ncores",
        group="hardware options",
        default="available",
        help=(
            "The maximum number of cores/threads to use in any step. "
            "Default: all available cores."
        ),
    )

    parser.add_argument(
        "SEAMM",
        "--memory",
        group="hardware options",
        default="available",
        help=(
            "The maximum amount of memory to use in any step, which can be "
            "'all' or 'available', or a number, which may use k, Ki, "
            "M, Mi, etc. suffixes. Default: available."
        ),
    )

    return parser

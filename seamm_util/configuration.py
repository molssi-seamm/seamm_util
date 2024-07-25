# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""A class for reading, updating and writing the configuration file.

This class handles the configuration (.ini) file as text, so that comments
in the file are preserved.
"""

from pathlib import Path


class Configuration(object):
    def __init__(self, path=None):
        self._path = None

        "A dictionary to save the text of the configuration file."
        self._data = {}

        # Set the path, which reads the file if it exsists
        self.path = path

    def __eq__(self, other):
        "Test if this configuration is equal to another in the sense of text."
        return str(self) == str(other)

    def __str__(self):
        """Create the text of the configuration file."""
        return self.to_string()

    @property
    def path(self):
        """The path to the configuration file."""
        return self._path

    @path.setter
    def path(self, value):
        if value is None:
            self._path = None
            self._data = {}
        else:
            new_path = Path(value).expanduser().resolve()
            if new_path != self._path:
                self._path = new_path
                if new_path.exists():
                    self._read()
                else:
                    self._data = {}

    def add_prolog(self, text="", force=False):
        """Add the prolog to the configuration.

        Parameters
        ----------
        text : str = ''
            The body of the prolog, which should be just comments.
        force : bool = True
            Whether to overwrite an existing prolog.
        """
        if "PROLOG" in self._data and not force:
            raise KeyError("The prolog already exists.")
        self._data["PROLOG"] = text.splitlines()

    def add_section(self, name, text="", force=False):
        """Add a new section to the configuration.

        Parameters
        ----------
        name : str
            The name of the section.
        text : str = ''
            The body of the section, which must be properly formatted.
        force : bool = True
            Whether to overwrite an existing section of the same name.
        """
        if self.section_exists(name) and not force:
            raise KeyError(f"Section '{name}' already exists.")
        section = name.lower()
        self._data[section] = [f"[{name}]"]
        lines = text.splitlines()
        if len(lines) > 0:
            tmp = lines[0].strip()
            if tmp[0] == "[" and tmp[-1] == "]":
                if tmp[1:-1] != name:
                    raise ValueError(
                        "Section name doesn't match: '{tmp[1:-1]}' vs '{name}'"
                    )
                lines = lines[1:]
        self._data[section].extend(lines)

    def file_exists(self):
        """Whether the configuration file exists."""
        if self.path is None:
            return False
        else:
            return self.path.exists()

    def from_string(self, text):
        """Replace the contents of the configuration with those from `text`.

        Parameters
        ----------
        text : str
            The configuration data as text.
        """
        self._data = {}
        section = "PROLOG"
        lines = []
        for line in text.splitlines():
            if len(line) > 0:
                # Look for a section name, like [<name>]
                tmp = line.strip()
                if tmp[0] == "[" and tmp[-1] == "]":
                    self._data[section] = lines
                    section = tmp[1:-1].lower()
                    lines = []
            lines.append(line)
        # Put the last section into the data
        self._data[section] = lines

    def get_prolog(self):
        """Return the prolog of the file, if any.

        Returns
        -------
        str
            The prolog of the configuration.
        """
        if "PROLOG" in self._data:
            result = "\n".join(self._data["PROLOG"]) + "\n"
        else:
            result = ""
        return result

    def get_values(self, section):
        """Return the values in a section as a dictionary.

        Returns an empty dictionary if the section does not exist, or if it
        does not contain any keyword definitions. Use `section_exists` to
        differentiate.

        Parameters
        ----------
        section : str
            The name of the section to retrieve.

        Returns
        -------
        dict
            A dictionary of keyword-value pairs, as strings.
        """
        result = {}
        if self.section_exists(section):
            for line in self._data[section.lower()]:
                line = line.strip()
                if len(line) > 0:
                    if line[0] == "#":
                        continue
                    if "=" in line:
                        key, value = line.split("=", maxsplit=1)
                        result[key.strip()] = value.strip()
        return result

    def _read(self):
        """Read the configuration file and split into sections."""
        self.from_string(self.path.read_text())

    def save(self):
        """Save the current configuration to disk."""
        self.path.write_text(str(self))

    def sections(self):
        """Return a list of sections in the configuration.

        Returns
        -------
        [str]
            The list of sections.
        """
        result = sorted(self._data.keys())
        if "PROLOG" in result:
            result.remove("PROLOG")
        if "seamm" in result:
            result.remove("seamm")
            result.insert(0, "seamm")
        if "default" in result:
            result.remove("default")
            result.insert(0, "default")
        return result

    def section_exists(self, section):
        """Return whether a section exits in the configuration.

        Parameters
        ----------
        section : str
            The name of the section.

        Returns
        -------
        bool
            True if the section exists; False otherwise.
        """
        return section is not None and section.lower() in self._data

    def set_value(self, section, key, value, strict=False):
        """Set the key in a section.

        Parameters
        ----------
        section : str
            The section to work with.
        key : str
            The key to set in the section.
        value : str
            The value to set the key to.
        strict : bool = False
            Raise an error is the key does not already exist.
        """
        lines = self._data[section.lower()]
        found = False
        i = 0
        for line in lines:
            if "=" in line:
                if line.strip().split("=", maxsplit=1)[0].strip() == key:
                    found = True
                    if value is None:
                        lines[i] = f"# {line}"
                    else:
                        lines[i] = f"{key} = {value}"
                    break
            i += 1

        if not found:
            if strict:
                raise KeyError(f"'{key}' not in section {section}.")
            else:
                # Maybe it is there but commented...
                found = False
                i = 0
                for line in lines:
                    line = line.lstrip("#").strip()
                    if "=" in line:
                        if line.split("=", maxsplit=1)[0].strip() == key:
                            found = True
                            if value is not None:
                                lines[i] = f"{key} = {value}"
                            break
                    i += 1
                if not found:
                    if value is None:
                        lines.append(f"# {key} = ")
                    else:
                        lines.append(f"{key} = {value}")

    def to_string(self, section=None):
        """Create the text of a section.

        Parameters
        ----------
        section : str
            The name of the section. Defaults to the entire file.
        """
        if section is None:
            result = []
            if "PROLOG" in self._data:
                result.extend(self._data["PROLOG"])
                if result[-1] != "":
                    result.append("")
            for section in self.sections():
                result.extend(self._data[section])
                if result[-1] != "":
                    result.append("")
        else:
            result = self._data[section.lower()]

        return "\n".join(result) + "\n"

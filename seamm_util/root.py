# -*- coding: utf-8 -*-

"""Where the SEAMM installation in use lives: its *root*.

The root holds an installation's configuration (``seamm.ini`` beside the codes'
``<code>.ini`` files), its data and its jobs. Several installations can live on one
machine (``~/SEAMM``, ``~/SEAMM_DEV``, ...), so the default root is taken from the
installation the running Python belongs to rather than fixed at ``~/SEAMM``.
"""

import os
from pathlib import Path
import sys

DEFAULT_ROOT = "~/SEAMM"


def installation_root(prefix=None):
    """The root of the SEAMM installation this Python belongs to, or None.

    An installation made by seamm-manager keeps its Python environments inside its
    root (``<root>/venv``, ``<root>/venv-webui``, or the versioned
    ``<root>/venvs/<stamp>`` that ``<root>/venv`` links to). If this interpreter's
    environment is such a directory, and the root holds a ``Jobs`` directory or
    ``.ini`` files, that directory is the root. Any other environment (a conda
    environment, a developer's scratch venv) gives None.

    Parameters
    ----------
    prefix : str or pathlib.Path = sys.prefix
        The environment to examine.

    Returns
    -------
    pathlib.Path or None
    """
    prefix = Path(sys.prefix if prefix is None else prefix)
    if prefix.parent.name == "venvs":
        # A versioned environment, <root>/venvs/<stamp> (seamm-manager keeps
        # <root>/venv as a link to the current one)
        root = prefix.parent.parent
    elif prefix.name.startswith("venv"):
        root = prefix.parent
    else:
        return None
    try:
        if (root / "Jobs").is_dir() or any(root.glob("*.ini")):
            return root
    except OSError:
        pass
    return None


def default_root():
    """The root to use when none is given on the command line.

    In order: the ``SEAMM_ROOT`` environment variable; the root of the installation
    this Python belongs to (see `installation_root`); ``~/SEAMM``. A root under the
    home directory is returned as ``~/...``.

    Returns
    -------
    str
    """
    value = os.environ.get("SEAMM_ROOT", "").strip()
    if value != "":
        return value
    root = installation_root()
    if root is None:
        return DEFAULT_ROOT
    try:
        return "~/" + str(root.relative_to(Path.home()))
    except ValueError:
        return str(root)


def current_root():
    """The root of the installation in use, as an absolute Path.

    The ``--root`` parsed for this run, when the SEAMM options have been parsed
    (a running flowchart, the JobServer, the editor); otherwise `default_root`.
    """
    root = None
    try:
        from .argument_parser import _parsers

        parser = _parsers.get("SEAMM")
        if parser is not None:
            root = parser.get_options("SEAMM").get("root")
    except Exception:
        root = None
    if root is None or str(root).strip() == "":
        root = default_root()
    return Path(root).expanduser()


def installation_path(*parts, root=None):
    """A path under the installation's root, falling back to ~/SEAMM's copy.

    Reference data (VASP potentials, forcefield files, ...) can live in each
    installation's root, but usually only the default installation ``~/SEAMM`` has
    it. This returns ``<root>/<parts>`` if it exists, else ``~/SEAMM/<parts>`` if
    that exists, else ``<root>/<parts>`` (where it would be created).

    Parameters
    ----------
    parts : str
        Path components under the root, e.g. "Parameters", "VASP".
    root : str or pathlib.Path = current_root()
        The installation's root.

    Returns
    -------
    pathlib.Path
    """
    root = current_root() if root is None else Path(root).expanduser()
    own = root.joinpath(*parts)
    if own.exists():
        return own
    fallback = Path(DEFAULT_ROOT).expanduser().joinpath(*parts)
    if fallback.exists():
        return fallback
    return own

# -*- coding: utf-8 -*-
"""The default root comes from SEAMM_ROOT, then the installation, then ~/SEAMM."""

import itertools
import logging
import sys

from seamm_util import root as root_module
from seamm_util.argument_parser import ArgumentParser, seamm_parser

_names = itertools.count()


def _installation(tmp_path, name="SEAMM_NEW", venv="venv", marker="Jobs"):
    root = tmp_path / name
    (root / venv).mkdir(parents=True)
    if marker == "Jobs":
        (root / "Jobs").mkdir()
    elif marker == "ini":
        (root / "mopac.ini").write_text("[local]\n")
    return root


def test_installation_root(tmp_path):
    root = _installation(tmp_path)
    assert root_module.installation_root(root / "venv") == root
    # A versioned environment made by seamm-manager
    assert root_module.installation_root(root / "venvs" / "2026-10-02T14-22-43") == root
    webui = _installation(tmp_path, "B", venv="venv-webui", marker="ini")
    assert root_module.installation_root(webui / "venv-webui") == webui
    bare = _installation(tmp_path, "C", marker=None)  # no Jobs, no .ini
    assert root_module.installation_root(bare / "venv") is None
    assert root_module.installation_root(tmp_path / "miniconda3/envs/seamm") is None


def test_default_root_order(tmp_path, monkeypatch):
    root = _installation(tmp_path)
    monkeypatch.setattr(sys, "prefix", str(root / "venv"))

    monkeypatch.setenv("SEAMM_ROOT", "/somewhere/else")
    assert root_module.default_root() == "/somewhere/else"

    monkeypatch.delenv("SEAMM_ROOT")
    assert root_module.default_root() == str(root)
    monkeypatch.setattr(root_module.Path, "home", lambda: tmp_path)
    assert root_module.default_root() == "~/SEAMM_NEW"

    monkeypatch.setattr(sys, "prefix", str(tmp_path / "miniconda3/envs/seamm"))
    assert root_module.default_root() == "~/SEAMM"


def _parse(tmp_path, ini_text=None):
    ini = tmp_path / "seamm.ini"
    if ini_text is not None:
        ini.write_text(ini_text)
    name = f"test-root-{next(_names)}"
    from seamm_util import argument_parser

    argument_parser._parsers[name] = ArgumentParser(ini_files=[str(ini)])
    parser = seamm_parser(name=name)
    return parser.parse_args([])["SEAMM"]["root"]


def test_parser_uses_installation_root(tmp_path, monkeypatch):
    monkeypatch.delenv("SEAMM_ROOT", raising=False)
    root = _installation(tmp_path)
    monkeypatch.setattr(sys, "prefix", str(root / "venv"))
    assert _parse(tmp_path) == str(root)


def test_seamm_root_beats_shared_ini(tmp_path, monkeypatch):
    monkeypatch.setenv("SEAMM_ROOT", "/from/env")
    assert _parse(tmp_path, "[SEAMM]\nroot = /from/ini\n") == "/from/env"


def test_ini_root_still_works_but_warns(tmp_path, monkeypatch, caplog):
    monkeypatch.delenv("SEAMM_ROOT", raising=False)
    with caplog.at_level(logging.WARNING):
        assert _parse(tmp_path, "[SEAMM]\nroot = /from/ini\n") == "/from/ini"
    assert "deprecated" in caplog.text


def test_current_root_prefers_parsed_option(tmp_path, monkeypatch):
    from seamm_util import argument_parser

    monkeypatch.setenv("SEAMM_ROOT", str(tmp_path / "from_env"))
    saved = argument_parser._parsers.pop("SEAMM", None)
    try:
        assert root_module.current_root() == tmp_path / "from_env"  # not parsed
        parser = ArgumentParser(ini_files=[])
        argument_parser._parsers["SEAMM"] = parser
        seamm_parser()  # defines the SEAMM options on the "SEAMM" parser
        parser.parse_args(["--root", str(tmp_path / "parsed")])
        assert root_module.current_root() == tmp_path / "parsed"
    finally:
        argument_parser._parsers.pop("SEAMM", None)
        if saved is not None:
            argument_parser._parsers["SEAMM"] = saved


def test_installation_path_falls_back_to_default_installation(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    new = home / "SEAMM_NEW"
    default = home / "SEAMM" / "Parameters" / "VASP"

    # Neither exists: the installation's own path
    assert root_module.installation_path("Parameters", "VASP", root=new) == (
        new / "Parameters" / "VASP"
    )
    # Only ~/SEAMM has it: fall back
    default.mkdir(parents=True)
    assert root_module.installation_path("Parameters", "VASP", root=new) == default
    # The installation has its own copy: use it
    (new / "Parameters" / "VASP").mkdir(parents=True)
    assert root_module.installation_path("Parameters", "VASP", root=new) == (
        new / "Parameters" / "VASP"
    )

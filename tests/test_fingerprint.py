#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the fingerprints of calculations' settings."""

from seamm_util.fingerprint import (
    calculation_record,
    geometry_fingerprint,
    hashed_version,
    normalize_lines,
)


def test_hashed_version():
    assert hashed_version("6.1.1") == "6.1"
    assert hashed_version("6.1") == "6.1"
    assert hashed_version("6") == "6"
    assert hashed_version(" 16 C.02 ") == "16 C.02"
    assert hashed_version("2026.10.28") == "2026.10"
    assert hashed_version(None) == ""


def test_normalize_lines():
    text = "! B3LYP   def2-SVP  # a comment\n\n  %scf\n MaxIter 200\nend\n"
    assert normalize_lines(text, comment="#", upper=True) == [
        "! B3LYP DEF2-SVP",
        "%SCF",
        "MAXITER 200",
        "END",
    ]
    assert normalize_lines("a  b\n\n c") == ["a b", "c"]


def test_patch_release_and_full_version():
    a = calculation_record("ORCA", "6.1.0", {"orca.inp": ["! B3LYP"]})
    b = calculation_record("ORCA", "6.1.1", {"orca.inp": "! B3LYP"})
    c = calculation_record("ORCA", "6.0.1", {"orca.inp": "! B3LYP"})
    assert a["fingerprint"] == b["fingerprint"]
    assert a["fingerprint"] != c["fingerprint"]
    assert b["version"] == "6.1.1" and b["hashed version"] == "6.1"
    assert b["fingerprint"].startswith("sha256:")
    g1 = calculation_record("Gaussian", "16 C.01", {}, hashed_version="16 C")
    g2 = calculation_record("Gaussian", "16 C.02", {}, hashed_version="16 C")
    assert g1["fingerprint"] == g2["fingerprint"] and g2["hashed version"] == "16 C"


def test_settings_and_program_matter():
    a = calculation_record("ORCA", "6.1", {"orca.inp": "! B3LYP"})
    assert (
        a["fingerprint"]
        != calculation_record("ORCA", "6.1", {"orca.inp": "! PBE0"})["fingerprint"]
    )
    assert (
        a["fingerprint"]
        != calculation_record("Psi4", "6.1", {"orca.inp": "! B3LYP"})["fingerprint"]
    )
    assert (
        a["fingerprint"]
        != calculation_record("ORCA", "6.1", {"other.inp": "! B3LYP"})["fingerprint"]
    )


def test_element_blocks():
    """Per-element blocks do not change the main fingerprint, and each element's
    fingerprint is the same whatever other elements are present."""
    h = "S 3\n13.01 0.0197"
    c = "S 6\n1238.4 0.0055"
    o = "S 6\n2266.2 0.0053"
    ethane = calculation_record(
        "ORCA", "6.1", {"orca.inp": "! B3LYP"}, element_blocks={"H": h, "C": c}
    )
    methanol = calculation_record(
        "ORCA",
        "6.1",
        {"orca.inp": "! B3LYP"},
        element_blocks={"H": h, "C": c, "O": o},
    )
    assert ethane["fingerprint"] == methanol["fingerprint"]
    for symbol in ("H", "C"):
        assert (
            ethane["element fingerprints"][symbol]
            == methanol["element fingerprints"][symbol]
        )
    assert "O" not in ethane["element fingerprints"]
    assert ethane["element fingerprints"]["H"] != ethane["element fingerprints"]["C"]


def test_geometry_fingerprint():
    z = [8, 1, 1]
    xyz = [[0.0, 0.0, 0.11730], [0.0, 0.75720, -0.46920], [0.0, -0.75720, -0.46920]]
    a = geometry_fingerprint(z, xyz)
    assert a == geometry_fingerprint(z, [[v + 1.0e-6 for v in p] for p in xyz])
    assert a == geometry_fingerprint(z, [[-0.0, 0.0, 0.1173]] + xyz[1:])
    assert a != geometry_fingerprint(z, [[0.0, 0.0, 0.1183]] + xyz[1:])
    assert a != geometry_fingerprint([8, 1, 9], xyz)
    record = calculation_record(
        "ORCA", "6.1", {"orca.inp": "! B3LYP"}, atomic_numbers=z, coordinates=xyz
    )
    assert record["geometry fingerprint"] == a
    assert calculation_record("ORCA", "6.1", {})["geometry fingerprint"] is None

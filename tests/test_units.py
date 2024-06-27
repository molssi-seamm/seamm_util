#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_util` package, units module."""

from seamm_util import Q_


def test_substance():
    """Testing that we can convert amounts of substance."""
    E = Q_(1.0, "mol")
    E2 = E.to("")
    assert f"{E:~} = {E2:~.4}" == "1.0 mol = 6.022e+23"


def test_inverse_substance():
    """Testing that we can convert amounts of substance."""
    E = Q_(6.022e23, "")
    E2 = E.to("mol")
    assert f"{E:~} = {E2:~.4}" == "6.022e+23 = 1.0 mol"


def test_energy():
    """Testing that we can convert amounts of substance."""
    E = Q_(1.0, "kcal/mol")
    E2 = E.to("eV")
    assert f"{E:~} = {E2:~.4}" == "1.0 kcal / mol = 0.04336 eV"


def test_inverse_energy():
    """Testing that we can convert amounts of substance."""
    E = Q_(1.0, "eV")
    E2 = E.to("kcal/mol")
    assert f"{E:~} = {E2:~.4}" == "1.0 eV = 23.06 kcal / mol"


def test_force():
    """Testing that we can convert amounts of substance."""
    E = Q_(1, "kcal/mol/angstrom")
    E2 = E.to("eV/angstrom")
    assert f"{E:~} = {E2:~.4}" == "1 kcal / Å / mol = 0.04336 eV / Å"


def test_inverse_force():
    """Testing that we can convert amounts of substance."""
    E = Q_(1, "eV/angstrom")
    E2 = E.to("kcal/mol/angstrom")
    assert f"{E:~} = {E2:~.4}" == "1 eV / Å = 23.06 kcal / Å / mol"

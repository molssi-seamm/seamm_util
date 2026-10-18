#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The atomic weights are mendeleev's (devtools/elemental_weights_from_mendeleev.py)."""

import pytest

from seamm_util import element_data

# The conventional values for elements whose weight varies in nature, and others
SPOT = {
    "H": 1.008,
    "Li": 6.94,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998403163,
    "Na": 22.98976928,
    "S": 32.06,
    "Cl": 35.45,
    "Ar": 39.948,
    "U": 238.02891,
    "Ra": 226.025408186,
}


@pytest.mark.parametrize("symbol", sorted(SPOT))
def test_spot_atomic_weights(symbol):
    assert element_data[symbol]["atomic weight"] == SPOT[symbol]


def test_the_table_matches_mendeleev():
    """Every atomic weight is mendeleev's: the standard atomic weight, or for an
    element without one the mass of its representative isotope."""
    pytest.importorskip("mendeleev")
    from mendeleev.fetch import fetch_table

    elements = fetch_table("elements")
    isotopes = fetch_table("isotopes")
    assert len(elements) == len(element_data)
    for _, row in elements.iterrows():
        w = float(row.atomic_weight)
        if abs(w - round(w)) < 1.0e-9:
            isotope = isotopes[
                (isotopes.atomic_number == row.atomic_number)
                & (isotopes.mass_number == int(round(w)))
            ]
            w = float(isotope.mass.iloc[0])
        assert element_data[row.symbol]["atomic weight"] == pytest.approx(
            w, rel=1e-12
        ), row.symbol

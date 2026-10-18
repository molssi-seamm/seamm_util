#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Elements with an interval of atomic weights use CIAAW's conventional value."""

import pytest

CONVENTIONAL = {
    "H": 1.008,
    "Li": 6.94,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "Mg": 24.305,
    "Si": 28.085,
    "S": 32.06,
    "Cl": 35.45,
    "Ar": 39.95,
    "Br": 79.904,
    "Tl": 204.38,
    "Pb": 207.2,
}


@pytest.mark.parametrize("symbol", sorted(CONVENTIONAL))
def test_conventional_atomic_weight(symbol):
    from seamm_util import element_data

    assert element_data[symbol]["atomic weight"] == CONVENTIONAL[symbol]

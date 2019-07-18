# -*- coding: utf-8 -*-

"""Localize the unit handling."""

import pint

# Unit handling!
ureg = pint.UnitRegistry(auto_reduce_dimensions=True)
pint.set_application_registry(ureg)
Q_ = ureg.Quantity
units_class = ureg('1 km').__class__

_d = pint.Context('chemistry')
_d.add_transformation(
    '[mass]/[substance]', '[mass]', lambda units, x: x / units.avogadro_number
)
ureg.add_context(_d)
ureg.enable_contexts('chemistry')

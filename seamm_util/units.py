# -*- coding: utf-8 -*-

"""Localize the unit handling."""

import pint

# Unit handling!
ureg = pint.UnitRegistry(auto_reduce_dimensions=True)
pint.set_application_registry(ureg)
Q_ = ureg.Quantity
units_class = ureg("1 km").__class__

_d = pint.Context("chemistry")

factor = ureg.mol / ureg.avogadro_number

_d.add_transformation("", "[substance]", lambda ureg, x: x * factor)
_d.add_transformation("[substance]", "", lambda ureg, x: x / factor)

_d.add_transformation("[mass]/[substance]", "[mass]", lambda ureg, x: x * factor)

_d.add_transformation(
    "[length] * [mass] / [substance] / [time] ** 2",
    "[length] * [mass] / [time] ** 2",
    lambda ureg, x: x * factor,
)
_d.add_transformation(
    "[length] * [mass] / [time] ** 2",
    "[length] * [mass] / [substance] / [time] ** 2",
    lambda ureg, x: x / factor,
)

_d.add_transformation(
    "[length] ** 2 * [mass] / [substance] / [time] ** 2",
    "[length] ** 2 * [mass] / [time] ** 2",
    lambda ureg, x: x * factor,
)
_d.add_transformation(
    "[length] ** 2 * [mass] / [time] ** 2",
    "[length] ** 2 * [mass] / [substance] / [time] ** 2",
    lambda ureg, x: x / factor,
)

ureg.add_context(_d)
ureg.enable_contexts("chemistry")


if __name__ == "__main__":  # pragma: no cover
    E = Q_(1.0, "kcal/mol")
    E2 = E.to("eV")
    print(f"{E:~} = {E2:~.4}")
    print()

    E2 = E.to("kJ/mol")
    print(f"{E:~} = {E2:~.4}")
    print()

    E = Q_(1.0, "eV")
    E2 = E.to("kcal/mol")
    print(f"{E:~} = {E2:~.4}")
    print()

    E2 = E.to("kJ/mol")
    print(f"{E:~} = {E2:~.4}")
    print()

    E = Q_(1.0, "mol")
    E2 = E.to("")
    print(f"{E:~} = {E2:~.4}")
    print()

    E = Q_(6.022e23, "")
    E2 = E.to("mol")
    print(f"{E:~} = {E2:~.4}")
    print()

    E = Q_(1, "kcal/mol/angstrom")
    E2 = E.to("eV/angstrom")
    print(f"{E:~} = {E2:~.4}")
    print()

    E = Q_(1, "eV/angstrom")
    E2 = E.to("kcal/mol/angstrom")
    print(f"{E:~} = {E2:~.4}")
    print()

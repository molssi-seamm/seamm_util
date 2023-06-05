# -*- coding: utf-8 -*-

"""Localize the unit handling."""

import pint

# Default units to use for a dimensionality
_default_units = {
    "[current] * [time]": [
        "e",
    ],
    "[current] * [length] * [time]": [
        "D",
        "e*Å",
        "e*a_0",
        "e*nm",
    ],
    "dimensionless": [
        "degree",
    ],
    "[length]": [
        "Å",
        "pm",
        "nm",
        "um",
        "a_0",
    ],
    "[length] ** 2": [
        "Å^2",
        "pm^2",
        "nm^2",
        "um^2",
        "a_0^2",
    ],
    "[length] ** 3": [
        "Å^3",
        "pm^3",
        "nm^3",
        "um^3",
        "a_0^2",
    ],
    "1 / [length]": [
        "1/Å",
        "1/pm",
        "1/nm",
        "1/um",
        "1/a_0",
    ],
    "[length] ** 2 * [mass]": [
        "10^-40*g*cm^2",
        "Da*Å^2",
        "Da*a_0^2",
    ],
    "[length] ** 2 * [mass] / [substance] / [time] ** 2": [
        "kJ/mol",
        "kcal/mol",
        "eV",
        "E_h",
        "Ry",
    ],
    "[length] ** 2 * [mass] / [time] ** 2": [
        "kJ/mol",
        "kcal/mol",
        "eV",
        "E_h",
        "Ry",
    ],
    "[length] * [mass] / [substance] / [time] ** 2": [
        "kcal/mol/Å",
        "kJ/mol/Å",
        "eV/Å",
    ],
    "[length] * [mass] / [time] ** 2": [
        "kcal/mol/Å",
        "kJ/mol/Å",
        "eV/Å",
    ],
    "[length] / [time] ** 2": [
        "m/s^2",
        "ft/s^2",
        "Å/fs^2",
    ],
    "[length] ** 2 * [mass] / [substance] / [temperature] / [time] ** 2": [
        "J/K/mol",
        "cal/K/mol",
    ],
    "[mass]": [
        "Da",
        "amu",
        "g",
        "kg",
        "tonne",
        "lb",
        "ton",
    ],
    "[mass] / [length] ** 3": [
        "g/mL",
        "kg/L",
        "kg/m^3",
        "g/mol/Å^3",
        "g/mol/A_0^3",
    ],
    "[mass] / [length] / [time] ** 2": [
        "Pa",
        "atm",
        "bar",
        "psi",
        "ksi",
    ],
    "[mass] / [time] ** 2": [
        "mdyne/Å",
        "N/m",
    ],
    "1 / [time] ** 2": [
        "mdyne/Å/Da",
        "N/m/Da",
    ],
    "[substance]": [
        "mol",
    ],
    "[temperature]": [
        "K",
        "°C",
        "°F",
        "°R",
    ],
    "[time]": [
        "fs",
        "ps",
        "ns",
        "us",
        "ms",
        "s",
    ],
}

# Unit handling!
ureg = pint.UnitRegistry(auto_reduce_dimensions=True)
ureg.default_format = "~P"
pint.set_application_registry(ureg)
Q_ = ureg.Quantity
units_class = ureg("1 km").__class__

_d = pint.Context("chemistry")

factor = ureg.mol / ureg.avogadro_number

_d.add_transformation("", "[substance]", lambda ureg, x: x * factor)
_d.add_transformation("[substance]", "", lambda ureg, x: x / factor)

_d.add_transformation("1 / [substance]", "", lambda ureg, x: x * factor)
_d.add_transformation("", "1 / [substance]", lambda ureg, x: x / factor)

_d.add_transformation("[mass] / [substance]", "[mass]", lambda ureg, x: x * factor)
_d.add_transformation("[mass]", "[mass] / [substance]", lambda ureg, x: x / factor)

# kJ/mol/Å --> eV/Å
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

# kJ/mol --> eV
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

# kJ/mol/K --> eV/K
_d.add_transformation(
    "[length] ** 2 * [mass] / [substance] / [temperature] / [time] ** 2",
    "[length] ** 2 * [mass] / [temperature] / [time] ** 2",
    lambda ureg, x: x * factor,
)
_d.add_transformation(
    "[length] ** 2 * [mass] / [temperature] / [time] ** 2",
    "[length] ** 2 * [mass] / [substance] / [temperature] / [time] ** 2",
    lambda ureg, x: x / factor,
)

# kJ/mol/Å^2 --> eV/Å^2
_d.add_transformation(
    "[mass] / [substance] / [time] ** 2",
    "[mass] / [time] ** 2",
    lambda ureg, x: x * factor,
)

# eV/Å^2 --> kJ/mol/Å^2
_d.add_transformation(
    "[mass] / [time] ** 2",
    "[mass] / [substance] / [time] ** 2",
    lambda ureg, x: x / factor,
)

# kJ/mol/Å^3 --> eV/Å^3
_d.add_transformation(
    "[mass] / [length] / [substance] / [time] ** 2",
    "[mass] / [length] / [time] ** 2",
    lambda ureg, x: x * factor,
)

# eV/Å^3 --> kJ/mol/Å^3
_d.add_transformation(
    "[mass] / [length] / [time] ** 2",
    "[mass] / [length] / [substance] / [time] ** 2",
    lambda ureg, x: x / factor,
)

# kJ/mol/Å^4 --> eV/Å^4
_d.add_transformation(
    "[mass] / [length] ** 2 / [substance] / [time] ** 2",
    "[mass] / [length] ** 2 / [time] ** 2",
    lambda ureg, x: x * factor,
)

# eV/Å^4 --> kJ/mol/Å^4
_d.add_transformation(
    "[mass] / [length] ** 2 / [time] ** 2",
    "[mass] / [length] ** 2 / [substance] / [time] ** 2",
    lambda ureg, x: x / factor,
)

# kJ/mol*Å^6 --> eV*Å^6
_d.add_transformation(
    "[length] ** 8 * [mass] / [substance] / [time] ** 2",
    "[length] ** 8 * [mass] / [time] ** 2",
    lambda ureg, x: x * factor,
)

# eV*Å^6 --> kJ/mol*Å^6
_d.add_transformation(
    "[length] ** 8 * [mass] / [time] ** 2",
    "[length] ** 8 * [mass] / [substance] / [time] ** 2",
    lambda ureg, x: x / factor,
)

ureg.add_context(_d)
ureg.enable_contexts("chemistry")


def default_units(units_or_dimensions):
    """Return the default units.

    Parameters
    ----------
    units_or_dimensions : str
        The units or dimensionality.

    Returns
    -------
    [str]
        The list of unit strings.
    """
    if units_or_dimensions == "all":
        result = []
        for values in _default_units.values():
            result.extend(values)
        return result

    if "[" in units_or_dimensions or units_or_dimensions == "dimensionless":
        dimensionality = units_or_dimensions
    else:
        dimensionality = str(Q_(units_or_dimensions).dimensionality)

    if dimensionality in _default_units:
        return _default_units[dimensionality]
    else:
        result = []
        try:
            for units in ureg.get_compatible_units(dimensionality):
                result.append(f"{units:~P}")
            tmp = "\n\t".join(result)
            print(
                f"Automatic defaults for '{units_or_dimensions}' ({dimensionality}) "
                f"\n\t{tmp}"
            )
        except Exception:
            print(
                f"Warning: can't handle units '{units_or_dimensions}' --> "
                f"{dimensionality} for default units."
            )
        return result


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

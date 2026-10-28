# -*- coding: utf-8 -*-

"""Fingerprints of the settings of a calculation.

A fingerprint says whether two stored results, e.g. the energies of the species
of a reaction, come from the same kind of calculation. It is a hash of the input
that a code was given, after the code's step has removed everything that does
not change the result -- the cores and memory, file names, printing -- and
everything that belongs to the species rather than to the calculation -- the
geometry, charge and multiplicity, and choices derived from them such as RHF or
UHF. What remains are the settings, including defaults the step resolved, so a
changed default changes the fingerprint.

Basis sets, auxiliary basis sets and ECPs written out per element are hashed
per element instead, since two species have different elements: ethane and
methanol at the same level must match. A reaction is consistent when its species
agree on the main fingerprint and on the element fingerprints of the elements
they share.

The step of each code knows its input, so it does the removing; the functions
here do the rest, so that every code hashes the same way::

    record = calculation_record(
        "ORCA", "6.1.1", {"orca.inp": cleaned_text}, element_blocks={"H": ...}
    )
    record["fingerprint"]   # 'sha256:...'

Only the major and minor version are hashed: a patch release should not make
every stored result incompatible. The full version is kept in the record.
"""

import hashlib
import json
import re

__all__ = [
    "calculation_record",
    "geometry_fingerprint",
    "hashed_version",
    "normalize_lines",
]


def _sha256(text):
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def hashed_version(version):
    """The part of a program's version that is hashed: major.minor.

    Parameters
    ----------
    version : str
        The full version, e.g. "6.1.1".

    Returns
    -------
    str
        E.g. "6.1". A version that is not dotted numbers, such as Gaussian's
        "16 C.02", is returned stripped: its step should say what to hash, with
        the ``hashed_version`` argument of :func:`calculation_record`.
    """
    if version is None:
        return ""
    version = str(version).strip()
    if re.fullmatch(r"\d+(\.\d+)*", version) is None:
        return version
    return ".".join(version.split(".")[:2])


# calculation_record() has an argument of the same name
_hashed_version = hashed_version


def normalize_lines(text, comment=None, upper=False):
    """Input text normalized for hashing: lines stripped, runs of white space
    made single spaces, blank lines and comments removed, and optionally upper
    case for codes whose input is case-insensitive.

    Parameters
    ----------
    text : str
        The text.
    comment : str or None
        The character starting a comment, e.g. "#"; None if there are none.
    upper : bool
        Whether to convert to upper case.

    Returns
    -------
    [str]
        The normalized lines.
    """
    lines = []
    for line in text.splitlines():
        if comment is not None and comment in line:
            line = line[: line.index(comment)]
        line = " ".join(line.split())
        if line == "":
            continue
        lines.append(line.upper() if upper else line)
    return lines


def geometry_fingerprint(atomic_numbers, coordinates, decimals=4):
    """A fingerprint of a geometry: the atomic numbers and the Cartesian
    coordinates (Å) rounded to ``decimals`` places, in the given order.

    Parameters
    ----------
    atomic_numbers : [int]
        The atomic numbers.
    coordinates : [[float]]
        The Cartesian coordinates in Å.
    decimals : int = 4
        The decimal places kept.

    Returns
    -------
    str
        'sha256:...'
    """
    parts = []
    for z, xyz in zip(atomic_numbers, coordinates):
        values = []
        for v in xyz:
            v = round(float(v), decimals)
            if v == 0:
                v = 0.0  # no -0.0
            values.append(f"{v:.{decimals}f}")
        parts.append(f"{int(z)} " + " ".join(values))
    return _sha256("\n".join(parts))


def calculation_record(
    program,
    version,
    files,
    element_blocks=None,
    atomic_numbers=None,
    coordinates=None,
    hashed_version=None,
):
    """The record of a calculation's settings, with its fingerprints.

    Parameters
    ----------
    program : str
        The program, e.g. "ORCA".
    version : str
        Its full version, e.g. "6.1.1".
    files : {str: str or [str]}
        The input files, by name, as text or lines, with what does not belong to
        the settings already removed by the code's step.
    element_blocks : {str: str or [str]}, optional
        The basis set, auxiliary basis or ECP data written out per element, by
        element symbol, removed from ``files``.
    atomic_numbers, coordinates : optional
        The geometry, for its fingerprint; see :func:`geometry_fingerprint`.
    hashed_version : str, optional
        The part of the version to hash, if not major.minor of a dotted version.

    Returns
    -------
    dict
        "program", "version" (full), "hashed version", "fingerprint" (the
        settings), "element fingerprints" ({symbol: fingerprint}), "geometry
        fingerprint" (or None), "files" and "element blocks" (the hashed text,
        for finding the cause of a mismatch).
    """
    version = "" if version is None else str(version).strip()
    short = _hashed_version(version) if hashed_version is None else hashed_version

    def as_text(value):
        if isinstance(value, (list, tuple)):
            return "\n".join(value)
        return str(value)

    texts = {name: as_text(value) for name, value in files.items()}
    payload = {"program": program, "version": short, "files": texts}
    fingerprint = _sha256(json.dumps(payload, sort_keys=True))

    blocks = {
        symbol: as_text(value) for symbol, value in (element_blocks or {}).items()
    }
    element_fingerprints = {
        symbol: _sha256(
            json.dumps(
                {"program": program, "version": short, "element": symbol, "text": text},
                sort_keys=True,
            )
        )
        for symbol, text in sorted(blocks.items())
    }

    if atomic_numbers is not None and coordinates is not None:
        geometry = geometry_fingerprint(atomic_numbers, coordinates)
    else:
        geometry = None

    return {
        "program": program,
        "version": version,
        "hashed version": short,
        "fingerprint": fingerprint,
        "element fingerprints": element_fingerprints,
        "geometry fingerprint": geometry,
        "files": texts,
        "element blocks": blocks,
    }

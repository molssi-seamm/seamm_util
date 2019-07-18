# -*- coding: utf-8 -*-

"""Functions for handling MDL molfiles"""

import logging
import time

logger = logging.getLogger(__name__)

integer_bond_order = {'single': 1, 'double': 2, 'triple': 3}
string_bond_order = ['', 'single', 'double', 'triple']


def from_seamm(structure, description='****', comment=''):
    """Transform a Seamm structure to MDL mol file, version 3"""
    lines = []

    atoms = structure['atoms']
    natoms = len(atoms['elements'])
    bonds = structure['bonds']
    nbonds = len(bonds)
    nsgroups = 0
    n3d = 0
    is_chiral = 0  # may need to think about this later.

    lines.append(description)
    date_time = time.strftime('%m%d%y%H%M')

    lines.append('PS' + 'SEAMM_WF' + date_time + '3D')
    if comment == '':
        lines.append('Generated from a SEAMM structure in a flowchart')
    else:
        lines.append(comment)
    lines.append('  0  0  0     0  0            999 V3000')

    lines.append('M  V30 BEGIN CTAB')
    lines.append(
        'M  V30 COUNTS {} {} {} {} {}'.format(
            natoms, nbonds, nsgroups, n3d, is_chiral
        )
    )
    lines.append('M  V30 BEGIN ATOM')
    count = 0
    for element, xyz in zip(atoms['elements'], atoms['coordinates']):
        count += 1
        x, y, z = xyz
        lines.append('M  V30 {} {} {} {} {} 0'.format(count, element, x, y, z))
    lines.append('M  V30 END ATOM')
    lines.append('M  V30 BEGIN BOND')
    count = 0
    for i, j, bond_order in bonds:
        count += 1
        lines.append(
            'M  V30 {} {} {} {}'.format(
                count, integer_bond_order[bond_order], i, j
            )
        )
    lines.append('M  V30 END BOND')
    lines.append('M  V30 END CTAB')
    lines.append('M  END')

    return '\n'.join(lines)


def to_seamm(data):
    """Transform from a MDL mol file, version 3 to a SEAMM structure"""

    n_molecules = 0
    lines = data.splitlines()

    lineno = 0
    # description = lines[lineno].strip()
    lineno += 1
    # header
    lineno += 1
    # comment
    lineno += 1
    if lines[lineno].split()[6] != 'V3000':
        raise RuntimeError(
            "molfile:to_seamm -- the file is not version 3: '" +
            lines[lineno] + "'"
        )
    lineno += 1
    while lineno < len(lines):
        line = lines[lineno]
        lineno += 1

        if 'M  V30 BEGIN CTAB' in line:
            n_molecules += 1
            atoms = {}
            atoms['elements'] = []
            atoms['coordinates'] = []
            bonds = []
        elif 'M  V30 COUNTS' in line:
            junk1, junk2, junk3, natoms, nbonds, nsgroups, n3d, is_chiral = \
                line.split()

            natoms = int(natoms)
            nbonds = int(nbonds)
            nsgroups = int(nsgroups)
            n3d = int(n3d)
            is_chiral = bool(is_chiral)

            line = lines[lineno]
            lineno += 1
            if 'M  V30 BEGIN ATOM' in line:
                last = lineno + natoms
                while lineno < last:
                    line = lines[lineno]
                    lineno += 1
                    junk1, junk2, i, symbol, x, y, z, q = line.split()
                    atoms['coordinates'].append((float(x), float(y), float(z)))
                    atoms['elements'].append(symbol)
            line = lines[lineno]
            lineno += 1
            if 'M  V30 END ATOM' not in line:
                raise RuntimeError("Missing end of atoms: '" + line + "'")
            line = lines[lineno]
            lineno += 1
            if 'M  V30 BEGIN BOND' in line:
                last = lineno + nbonds
                while lineno < last:
                    line = lines[lineno]
                    lineno += 1
                    junk1, junk2, i, bond_order, iatom, jatom = line.split()
                    bonds.append(
                        (
                            int(iatom), int(jatom),
                            string_bond_order[int(bond_order)]
                        )
                    )
                line = lines[lineno]
                lineno += 1
                if 'M  V30 END BOND' not in line:
                    raise RuntimeError("Missing end of bonds: '" + line + "'")
            elif nbonds > 0:
                raise RuntimeError("Missing bonds: '" + line + "'")

    structure = {'atoms': atoms, 'bonds': bonds}

    return structure

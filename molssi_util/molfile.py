# -*- coding: utf-8 -*-
"""Functions for handling MDL molfiles"""

import logging
import time

logger = logging.getLogger(__name__)

integer_bond_order = {'single': 1, 'double': 2, 'triple': 3}


def from_molssi(structure):
    """Transform a MolSSI structure to MDL mol file, version 3"""
    lines = []

    atoms = structure['atoms']
    natoms = len(atoms['elements'])
    bonds = structure['bonds']
    nbonds = len(bonds)
    nsgroups = 0
    n3d = 0
    is_chiral = 0  # may need to think about this later.

    lines.append('')
    date_time = time.strftime('%m%d%y%H%M')

    lines.append('PS' + 'MolSSIWF' + date_time + '3D')
    lines.append('Generated from a MolSSI structure in a workflow')
    lines.append('  0  0  0     0  0            999 V3000')

    lines.append('M  V30 BEGIN CTAB')
    lines.append('M  V30 COUNTS {} {} {} {} {}'.format(
        natoms, nbonds, nsgroups, n3d, is_chiral))
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
        lines.append('M  V30 {} {} {} {}'.format(
            count, integer_bond_order[bond_order], i, j))
    lines.append('M  V30 END BOND')
    lines.append('M  V30 END CTAB')
    lines.append('M  END')

    return '\n'.join(lines)

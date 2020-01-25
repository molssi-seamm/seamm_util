# -*- coding: utf-8 -*-

"""Functions for handling PDB files"""

import logging
import pprint
import time

logger = logging.getLogger(__name__)

integer_bond_order = {'single': 1, 'double': 2, 'triple': 3}


def from_molssi(structure):
    """Transform a MolSSI structure to PDB file"""
    lines = []

    atoms = structure['atoms']
    natoms = len(atoms['elements'])
    bonds = structure['bonds']

    date_time = time.strftime('%m%d%y%H%M')

    lines.append('COMPND    UNNAMED')
    lines.append('AUTHOR    MolSSI framework at ' + date_time)

    # atoms
    count = 0
    for element, xyz in zip(atoms['elements'], atoms['coordinates']):
        count += 1
        x, y, z = xyz
        lines.append(
            'ATOM  {:5d} {:>2s}   UNL A   1    '.format(count, element) +
            '{:8.3f}{:8.3f}{:8.3f}'.format(x, y, z) +
            '  1.00  0.00         {:>2s}'.format(element)
        )

    # bonds
    connections = [[]] * (natoms + 1)
    for i, j, bond_order in bonds:
        connections[i].append('{:5d}'.format(j))
        connections[j].append('{:5d}'.format(i))

    for i in range(1, natoms + 1):
        lines.append('CONECT{:5d}'.format(i) + ''.join(connections[i]))

    lines.append(
        'MASTER        0    0    0    0    0    0    0    0'
        '{:5d}    0{:5d}'.format(natoms, natoms)
    )
    lines.append('END')

    return '\n'.join(lines)


def to_molssi(data):
    """Convert a pdb file to the MolSSI internal structure

    For complete documentation, see
    http://www.wwpdb.org/documentation/file-format-content/format33/v3.3.html

    Order of records:

    RECORD TYPE             EXISTENCE           CONDITIONS IF  OPTIONAL
    --------------------------------------------------------------------------------------
    HEADER                  Mandatory
    OBSLTE                  Optional            Mandatory in  entries that have been
                                                replaced by a newer entry.
    TITLE                   Mandatory
    SPLIT                   Optional            Mandatory when  large macromolecular
                                                complexes  are split into multiple PDB
                                                entries.
    CAVEAT                  Optional            Mandatory when there are outstanding  errors
                                                such  as chirality.
    COMPND                  Mandatory
    SOURCE                  Mandatory
    KEYWDS                  Mandatory
    EXPDTA                  Mandatory
    NUMMDL                  Optional            Mandatory for  NMR ensemble entries.
    MDLTYP                  Optional            Mandatory for  NMR minimized average
                                                Structures or when the entire  polymer
                                                chain contains C alpha or P atoms only.
    AUTHOR                  Mandatory
    REVDAT                  Mandatory
    SPRSDE                  Optional            Mandatory for a replacement entry.
    JRNL                    Optional            Mandatory for a publication describes
                                                the experiment.
    REMARK 0                Optional            Mandatory for a re-refined structure
    REMARK 1                Optional
    REMARK 2                Mandatory
    REMARK 3                Mandatory
    REMARK N                Optional            Mandatory under certain conditions.
    DBREF                   Optional            Mandatory for all polymers.
    DBREF1/DBREF2           Optional            Mandatory when certain sequence  database
                                                accession  and/or sequence numbering
                                                does  not fit preceding DBREF format.
    SEQADV                  Optional            Mandatory if sequence  conflict exists.
    SEQRES                  Mandatory           Mandatory if ATOM records exist.
    MODRES                  Optional            Mandatory if modified group exists  in the
                                                coordinates.
    HET                     Optional            Mandatory if a non-standard group other
                                                than water appears in the coordinates.
    HETNAM                  Optional            Mandatory if a non-standard group other
                                                than  water appears in the coordinates.
    HETSYN                  Optional
    FORMUL                  Optional            Mandatory if a non-standard group or
                                                water appears in the coordinates.
    HELIX                   Optional
    SHEET                   Optional
    SSBOND                  Optional            Mandatory if a  disulfide bond is present.
    LINK                    Optional            Mandatory if  non-standard residues appear
                                                in a  polymer
    CISPEP                  Optional
    SITE                    Optional
    CRYST1                  Mandatory
    ORIGX1 ORIGX2 ORIGX3    Mandatory
    SCALE1 SCALE2 SCALE3    Mandatory
    MTRIX1 MTRIX2 MTRIX3    Optional            Mandatory if  the complete asymmetric unit
                                                must  be generated from the given coordinates
                                                using non-crystallographic symmetry.
    MODEL                   Optional            Mandatory if more than one model
                                                is  present in the entry.
    ATOM                    Optional            Mandatory if standard residues exist.
    ANISOU                  Optional
    TER                     Optional            Mandatory if ATOM records exist.
    HETATM                  Optional            Mandatory if non-standard group exists.
    ENDMDL                  Optional            Mandatory if MODEL appears.
    CONECT                  Optional            Mandatory if non-standard group appears
                                                and  if LINK or SSBOND records exist.
    MASTER                  Mandatory
    END                     Mandatory

    Description of HETATM records:

    COLUMNS       DATA  TYPE     FIELD         DEFINITION
    -----------------------------------------------------------------------
     1 - 6        Record name    "HETATM"
     7 - 11       Integer        serial        Atom serial number.
    13 - 16       Atom           name          Atom name.
    17            Character      altLoc        Alternate location indicator.
    18 - 20       Residue name   resName       Residue name.
    22            Character      chainID       Chain identifier.
    23 - 26       Integer        resSeq        Residue sequence number.
    27            AChar          iCode         Code for insertion of residues.
    31 - 38       Real(8.3)      x             Orthogonal coordinates for X.
    39 - 46       Real(8.3)      y             Orthogonal coordinates for Y.
    47 - 54       Real(8.3)      z             Orthogonal coordinates for Z.
    55 - 60       Real(6.2)      occupancy     Occupancy.
    61 - 66       Real(6.2)      tempFactor    Temperature factor.
    77 - 78       LString(2)     element       Element symbol; right-justified.
    79 - 80       LString(2)     charge        Charge on the atom.

    Description of CONECT records:

    COLUMNS       DATA  TYPE      FIELD        DEFINITION
    -------------------------------------------------------------------------
     1 -  6        Record name    "CONECT"
     7 - 11        Integer        serial       Atom  serial number
    12 - 16        Integer        serial       Serial number of bonded atom
    17 - 21        Integer        serial       Serial  number of bonded atom
    22 - 26        Integer        serial       Serial number of bonded atom
    27 - 31        Integer        serial       Serial number of bonded atom
    """  # noqa: E501

    # Initialize the structure
    structure = {}
    structure['periodicity'] = 0
    atoms = structure['atoms'] = {}
    names = atoms['names'] = []
    elements = atoms['elements'] = []
    coordinates = atoms['coordinates'] = []
    units = structure['units'] = {}
    units['coordinates'] = 'angstrom'
    bonds = structure['bonds'] = []

    connections = None

    if isinstance(data, list):
        lines = data
    else:
        lines = data.split('\n')

    for line in lines:
        key = line[0:6].rstrip()
        if key == 'HEADER':
            pass
        elif key == 'OBSLTE':
            pass
        elif key == 'TITLE':
            pass
        elif key == 'SPLIT':
            pass
        elif key == 'CAVEAT':
            pass
        elif key == 'COMPND':
            pass
        elif key == 'SOURCE':
            pass
        elif key == 'KEYWDS':
            pass
        elif key == 'EXPDTA':
            pass
        elif key == 'NUMMDL':
            pass
        elif key == 'MDLTYPE':
            pass
        elif key == 'AUTHOR':
            pass
        elif key == 'REVDAT':
            pass
        elif key == 'SPRSDE':
            pass
        elif key == 'JRNL':
            pass
        elif key == 'REMARK':
            pass
        elif key == 'DBREF':
            pass
        elif key == 'DBREF1':
            pass
        elif key == 'DBREF2':
            pass
        elif key == 'SEQADV':
            pass
        elif key == 'SEQRES':
            pass
        elif key == 'MODRES':
            pass
        elif key == 'HET':
            pass
        elif key == 'HETNAM':
            pass
        elif key == 'HETSYN':
            pass
        elif key == 'FORMUL':
            pass
        elif key == 'HELIX':
            pass
        elif key == 'SHEET':
            pass
        elif key == 'SSBOND':
            pass
        elif key == 'LINK':
            pass
        elif key == 'CISPEP':
            pass
        elif key == 'SITE':
            pass
        elif key == 'CRYST1':
            pass
        elif key == 'ORIGX1':
            pass
        elif key == 'ORIGX2':
            pass
        elif key == 'ORIGX3':
            pass
        elif key == 'SCALE1':
            pass
        elif key == 'SCALE2':
            pass
        elif key == 'SCALE3':
            pass
        elif key == 'MTRIX1':
            pass
        elif key == 'MTRIX2':
            pass
        elif key == 'MTRIX3':
            pass
        elif key == 'MODEL':
            pass
        elif key == 'ATOM' or key == 'HETATM':
            # serial = int(line[6:11])  # noqa: F841
            name = line[12:16].strip()
            # altloc = line[16]  # noqa: F841
            # resname = line[17:20].strip()  # noqa: F841
            # chainid = line[21]  # noqa: F841
            # resseq = int(line[22:26])  # noqa: F841
            # icode = line[26]  # noqa: F841
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            # tmp = line[54:60].strip()
            # occupancy = 0.0 if tmp == '' else float(tmp)  # noqa: F841
            # tmp = line[60:66].strip()
            # tempfactor = 0.0 if tmp == '' else float(tmp)  # noqa: F841
            element = line[75:78].strip()
            # tmp = line[78:80].strip()
            # charge = 0.0 if tmp == '' else float(tmp)  # noqa: F841

            names.append(name)
            elements.append(element)
            coordinates.append((x, y, z))
        elif key == 'ANISOU':
            pass
        elif key == 'TER':
            pass
        elif key == 'ENDMDL':
            pass
        elif key == 'CONECT':
            if connections is None:
                natoms = len(elements)
                connections = [] * (natoms + 1)

            atom = int(line[6:11])
            for tmp in line[11:31].split():
                if tmp.trim() != '':
                    connections[atom].append(int(tmp))
        elif key == 'MASTER':
            pass
        elif key == 'END':
            break
        else:
            raise RuntimeError('Illegal line in PDB file\n\t' + line)

    if connections is not None:
        for i in range(1, natoms + 1):
            for j in connections[i]:
                if i not in connections[j]:
                    logger.warning(
                        'Bond {}-{} not found in PDB file'.format(j, i)
                    )
                    # put in the bond since we won't see its partner!
                    if i > j:
                        bonds.append((j, i, 0))
                    else:
                        bonds.append((i, j, 0))
                elif i < j:
                    # put in only 1 of 2 eqiuvalent bonds
                    bonds.append((i, j, 0))

    logger.debug('\n***Structure dict\n' + pprint.pformat(structure))

    return structure

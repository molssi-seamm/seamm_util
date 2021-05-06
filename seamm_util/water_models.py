# -*- coding: utf-8 -*-

"""Various water models."""

import math

import seamm_util


class Water(object):
    """Generic water model"""

    def __init__(self, r0, theta0, qO=None, qH=None, lj_a=None, lj_b=None):
        """Initialize the basic water model

        Parameters
        ----------
        r0 : float
            The O-H bond-length
        theta0 : float
            The H-O-H angle, in degrees
        qO : float, optional
            The point charge on the oxygen, defaults to None
        qH : float, optional
            The point charge on the hydrogens, defaults to None
        """
        self.r0 = r0
        self.theta0 = theta0
        self.qO = qO
        self.qH = qH
        self.lj_a = lj_a
        self.lj_b = lj_b

    @staticmethod
    def create_model(model_name):
        """Static method to simplify constructing models for string names."""
        name = model_name.lower()
        if name == "spc":
            return SPC()
        if name == "spce" or name == "spc/e":
            return SPC_E()
        if name == "tip3p":
            return TIP3P()

        raise ValueError(
            "Water model '{}' not implemented or recognized.".format(model_name)
        )

    @staticmethod
    def find_waters(system):
        """Find the water molecules in the given system.

        At the moment, the atoms are 0-based, but the bonds are given using
        1-based atom numbers!

        Parameters
        ----------
        system : System object

        Returns
        -------

        """
        elements = system["atoms"]["elements"]
        n_atoms = len(elements)

        # List the bonds, ordering the two atoms.
        bonds = []
        for i, j, order in system["bonds"]:
            i -= 1
            j -= 1
            if i < j:
                bonds.append((i, j))
            else:
                bonds.append((j, i))

        # atoms bonded to each atom i
        bonded_to = []
        for i in range(n_atoms):
            bonded_to.append([])
        for i, j in bonds:
            bonded_to[i].append(j)
            bonded_to[j].append(i)

        n_bonds = []
        for i in range(n_atoms):
            bonded_to[i].sort()
            n_bonds.append(len(bonded_to[i]))

        # Now find water molecules by looking for an O attached to two H's
        waters = []
        for i in range(n_atoms):
            if elements[i] == "O" and n_bonds[i] == 2:
                h1, h2 = bonded_to[i]
                if (
                    elements[h1] == "H"
                    and n_bonds[h1] == 1
                    and elements[h2] == "H"
                    and n_bonds[h2] == 1
                ):
                    if h1 < h1:
                        waters.append((i, h1, h2))
                    else:
                        waters.append((i, h2, h1))
        return waters

    @property
    def mass(self):
        mass_oxygen = seamm_util.element_data["O"]["atomic weight"]
        mass_hydrogen = seamm_util.element_data["H"]["atomic weight"]

        return mass_oxygen + 2 * mass_hydrogen

    def coordinates(self):
        """A standard set of coordinates in Angstrom

        The oxygen is at the origin, with the hydrogens in the x-z plane.
        Z is the two-fold axis of symmetry.

        Returns
        -------
        Tuple of three tuples with (x, y z)
        """
        # H locations are ±x, 0, z
        x = self.r0 * math.sin(math.radians(self.theta0 / 2))
        z = self.r0 * math.cos(math.radians(self.theta0 / 2))

        return ((0.0, 0.0, 0.0), (x, 0.0, z), (-x, 0.0, z))

    def pdb(self):
        """The contents of a PDB file for this model.

        Returns
        -------
        pdb : str
            The contents of a PDB file for this model.
        """
        # H locations are ±x, 0, z
        x = self.r0 * math.sin(math.radians(self.theta0 / 2))
        z = self.r0 * math.cos(math.radians(self.theta0 / 2))

        string = (
            "COMPND      Water\n"
            "HETATM    1  O           1       0.000   0.000   0.000  1.00  0.00\n"  # noqa: E501
            "HETATM    2  H           1       {x:.3f}   0.000   {z:.3f}  1.00  0.00\n"  # noqa: E501
            "HETATM    3  H           1      -{x:.3f}   0.000   {z:.3f}  1.00  0.00\n"  # noqa: E501
            "TER       4              1 \n"
            "END"
        )

        return string.format(x=x, z=z)

    def system(self):
        """Return the model as a SEAMM system.

        Returns
        -------
        system : SEAMM system
        """
        system = {
            "periodicity": 0,
            "atoms": {
                "names": ["O", "H1", "H2"],
                "elements": ["O", "H", "H"],
                "coordinates": list(self.coordinates()),
                "charges": {"*": [self.qO, self.qH, self.qH]},
                "formal charges": [0, 0, 0],
                "atom_types": {"*": self.atom_types()},
            },
            "bonds": [(1, 2, "single"), (1, 3, "single")],
            "units": {"coordinates": "angstrom"},
        }  # yapf: disable
        return system


class SPC(Water):
    def __init__(self):
        super().__init__(1.0, 109.47, -0.82, 0.41)

    def atom_types(self):
        """The atom types for this model.

        Returns
        -------
        types : str[3]
            3-vector of atom types
        """
        return ["o_spc", "h_spc", "h_spc"]


class SPC_E(Water):
    def __init__(self):
        super().__init__(1.0, 109.47, -0.8476, 0.4238)

    def atom_types(self):
        """The atom types for this model.

        Returns
        -------
        types : str[3]
            3-vector of atom types
        """
        return ["o_spc/e", "h_spc/e", "h_spc/e"]

    def reference(self):
        ris = """
            TY  - JOUR
            T1  - The missing term in effective pair potentials
            AU  - Berendsen, H. J. C.
            AU  - Grigera, J. R.
            AU  - Straatsma, T. P.
            Y1  - 1987/11/01
            PY  - 1987
            DA  - 1987/11/01
            N1  - doi: 10.1021/j100308a038
            DO  - 10.1021/j100308a038
            T2  - The Journal of Physical Chemistry
            JF  - The Journal of Physical Chemistry
            JO  - J. Phys. Chem.
            SP  - 6269
            EP  - 6271
            VL  - 91
            IS  - 24
            PB  - American Chemical Society
            SN  - 0022-3654
            M3  - doi: 10.1021/j100308a038
            UR  - https://doi.org/10.1021/j100308a038
            ER  -
        """
        return ris


class TIP3P(Water):
    def __init__(self):
        super().__init__(0.9572, 104.52, -0.834, 0.417)

    def atom_types(self):
        """The atom types for this model.

        Returns
        -------
        types : str[3]
            3-vector of atom types
        """
        return ["o_tip3p", "h_tip3p", "h_tip3p"]

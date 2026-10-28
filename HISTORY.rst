=======
History
=======
2026.10.28 -- Bugfix: pint 0.26 broke the chemistry unit conversions
    * With pint 0.26 (released 2026-10-19) every conversion between per-molecule and
      per-mole quantities through SEAMM's "chemistry" context -- eV and kcal/mol or
      kJ/mol, eV/Å and kcal/mol/Å, molecules and mol -- failed with a RecursionError.
      seamm_util now requires pint < 0.26 until the context is made to work with it.

2026.10.18 -- Bugfix: atomic weights from mendeleev
    * For the elements whose weight varies in nature, the atomic weights were the
      midpoints of CIAAW's intervals rather than the conventional values: Li 6.9675
      instead of 6.94 (+0.4%), Ar 39.8775 instead of 39.948 (-0.18%), and B, S, C, O,
      Mg, Cl and Tl by 0.03% or less. The atomic weights now come from mendeleev: the
      standard atomic weights at full precision (F 18.998403163 rather than 18.998), the
      conventional values for those elements, and for elements with no standard atomic
      weight the mass of the representative isotope (Ra-226 226.025408186). Masses and
      densities change slightly, by up to 0.01% for most elements; 1000 argon atoms in
      47597 Å^3 now have a density of 1.3937 g/mL, not 1.3912.
    * This is the one table of element data: molsystem uses it too.
      devtools/elemental_weights_from_mendeleev.py regenerates the atomic weights and a
      test checks them against mendeleev.
    * LAMMPS takes its masses from this table when the forcefield has none, as for a
      machine-learned potential, so such MD with lithium ran with Li 0.4% too heavy.

2026.10.2 -- Bugfix: the default root for a versioned environment
    * seamm-manager now keeps an installation's Python environment in
      ``<root>/venvs/<date and time>``, with ``<root>/venv`` a link to the current one, and
      runs everything from the real path. A Python in such an environment now belongs to
      that installation, so ``run_flowchart`` and the apps run by hand from it use its
      root rather than ``~/SEAMM``.

2026.9.27.1 -- Helpers for finding an installation's files
    * ``seamm_util.current_root()`` gives the root of the installation in use: the
      ``--root`` parsed for this run if there is one, otherwise the default root.
    * ``seamm_util.installation_path(*parts)`` gives a path under that root, falling
      back to the default installation's copy in ``~/SEAMM`` when the installation has
      none. Plug-ins use it for reference data such as the VASP potentials, so a second
      installation works without copying them but can still have its own.

2026.9.27 -- The default root follows the installation
    * The default for ``--root`` was always ``~/SEAMM``, so a second installation such
      as ``~/SEAMM_DEV`` read ``~/SEAMM``'s configuration and data unless every command
      was given ``--root``. The default is now the ``SEAMM_ROOT`` environment variable if
      set, otherwise the installation the running Python belongs to (a seamm-manager
      environment ``<root>/venv`` whose root holds ``Jobs`` or ``.ini`` files), and
      otherwise ``~/SEAMM`` as before. Existing single installations behave exactly as
      they did.
    * ``root`` in the ``[SEAMM]`` section of ``~/.seamm.d/seamm.ini`` still works but
      logs a deprecation warning, since that file is shared by every installation of a
      user; ``SEAMM_ROOT`` takes precedence over it.
    * New functions ``seamm_util.default_root()`` and ``seamm_util.installation_root()``.

2026.9.18 -- Bugfix: pip metadata lacked requests
    * ``pip install seamm-util`` did not install ``requests``, which the Zenodo
      client imports, so seamm-util failed to import outside a conda-forge environment
      (whose recipe already listed it). It is now an install requirement.

2026.7.26 -- Support anonymous access to public Zenodo records
    * Added ``Zenodo.get_latest_public_record()``, which resolves a stable
      "concept" record id to whichever version of a public record is
      currently newest, with no authentication -- for "always fetch the
      current data" without hardcoding a version number.
    * Fixed ``Record.download_file()``, ``.get_file()``, and ``.files()``,
      which only recognized the authenticated deposit/edit API's file-entry
      shape (``filename``/``links.download``). The public records API uses
      ``key``/``links.self`` instead; these methods now accept either, so a
      ``Record`` from ``get_latest_public_record()`` works correctly.

2026.7.20 -- Internal: exclude _version.py from black
    * Excluded the generated ``_version.py`` from the ``black`` lint/format
      targets in the Makefile, matching the other SEAMM packages, so ``make
      lint`` no longer flags it. No effect on the installed package.

2026.7.15 -- Added a database-timeout option
    * Added the "database-timeout" option (default 20 seconds) that controls how
      long SEAMM waits for the job database when it is locked by another job
      before giving up. This helps when many jobs start at the same time, for
      example a batch of jobs on a cluster.

2025.12.9 -- Added transformation for density using g/mol/Å^3

2025.9.10 -- Added velocity units for speed of sound

2025.8.27 -- Added more pressure units
    * Added MPa, GPa, and TPa to the default pressure units.
    * Added units for 1/pressure and 1/temperature to support the thermomechanical step.
      
2025.8.18 -- Added ability to output graphs to several formats
    * Added graph output to HTML, PNG, JPEG, webp, SVG, and PDF

2024.8.22 -- Bugfix: charts with multiple exes, plus units for force constants
    * Add units for force constants (kJ/mol/Å^2,...)
    * Fixed an issue naming axes in plots with multiple axes
      
2024.8.1 -- Added default units for viscosity and fixed a bug in handling dimensions
    * Added more default units: dynamic viscosity (cP, etc) and kinematic viscosity
      (cSt, etc)
    * Fixed a bug handling unit dimensions since the order changed in Pint. Now they are
      put in a standard alphabetical order.

2024.7.25 -- Added configuration file handler
    * Added a configuration file handler that preserves comments in the file so that
      documentation is not stripped.
      
2024.7.15 -- Added temperature-energy conversions
    * Added conversions from temeprature units, like K, to energy, like kJ/mol and vice
      versa.
    * Used more of the Pint contexts, which should allow wavenumbers to frequency, etc.
      
2024.6.27 -- Added support for URI's
    * Now recognize URI's in the form local:path/to/file
    * An optional URI handler can be passed in to resolve such URI's.
      
2024.6.5 -- Bugfix: Handling of duplicates in lists
    * Roundoff in floating point numbers caused some duplicates to be missed. The code
      now checks for duplicates in a more robust way.
      
2024.4.30 -- Added utility for handling list definitions
    * Add list_definition.py with parse_list()
    * Updated makefile for doctests.

2024.4.26 -- Removed debug printing
    * Some debug printing was accidentally left in the code.
      
2024.4.22 -- Moving user preferences to ~/.seamm.d
    * To better support Docker, moving ~/.seammrc to ~/.seamm.d/seamrc
    * Moved seamm.ini from ~/SEAMM to ~/seamm.d since it only contains personal preferences.

2023.11.12 -- Internal update
    * Versioneer needed to be updated to account for changes in configparser.

2023.11.11 -- Updated for changes in Zenodo
    * Zenodo updated and made small changes to their API, which required changes in
      SEAMM.
    * Consolidated all private information about the user and their keys for Zenodo in
      ~/.seammrc

2023.6.4 -- Added more unit conversions to support thermochemistry
  * added E_h/K --> kJ/mol/K

2023.4.6 -- Added more unit conversions to support Buckingham potentials
  * added e.g. eV*Å^6 to kcal/mol*Å^6 to support Buckingham pontetials
    
2023.2.28 -- Added a compact JSON encoder
  * To make the schema-type JSON more human-readable.
    
2022.11.3 -- More conversions involving substance (mol) to number
  * Added energy/mol/Å^2 --> energy/Å^2 for force constants
  * Added energy/mol/Å^3 --> energy/Å^3 for stress/pressure/elastic constants

0.1.0 (2017-12-07)
  * First release on PyPI.

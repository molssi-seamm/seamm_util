=======
History
=======
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

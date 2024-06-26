=======
History
=======
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

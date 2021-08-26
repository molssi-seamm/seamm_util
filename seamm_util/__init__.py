# -*- coding: utf-8 -*-

"""
seamm_util
Utility functions for the SEAMM environment.
"""

# Bring up the classes so that they appear to be directly in
# the seamm_util package.

from seamm_util.argument_parser import getParser  # noqa: F401
from seamm_util.argument_parser import seamm_parser  # noqa: F401
from seamm_util.elemental_data import element_data  # noqa: F401
from seamm_util.check_executable import check_executable  # noqa: F401
from seamm_util.dictionary import Dictionary  # noqa: F401
from seamm_util.units import ureg, Q_, units_class  # noqa: F401
from seamm_util.include_open import Open  # noqa: F401
from seamm_util.include_open import splitext  # noqa: F401
from seamm_util.seamm_json import JSONDecoder  # noqa: F401
from seamm_util.seamm_json import JSONEncoder  # noqa: F401
from seamm_util.plotting import Figure  # noqa: F401
import seamm_util.printing  # noqa: F401
import seamm_util.variable_names  # noqa: F401
import seamm_util.water_models  # noqa: F401
import seamm_util.zenodo  # noqa: F401
from seamm_util.zenodo import Zenodo  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions

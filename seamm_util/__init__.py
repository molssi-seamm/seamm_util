# -*- coding: utf-8 -*-

"""
seamm_util
Utility functions for the SEAMM environment.
"""

# Bring up the classes so that they appear to be directly in
# the seamm_util package.

from .argument_parser import getParser  # noqa: F401
from .argument_parser import seamm_parser  # noqa: F401
from .compact_json_encoder import CompactJSONEncoder  # noqa: F401
from .elemental_data import element_data  # noqa: F401
from .check_executable import check_executable  # noqa: F401
from .dictionary import Dictionary  # noqa: F401
from .units import ureg, Q_, units_class, default_units  # noqa: F401
from .include_open import Open  # noqa: F401
from .include_open import splitext  # noqa: F401
from .seamm_json import JSONDecoder  # noqa: F401
from .seamm_json import JSONEncoder  # noqa: F401
from .plotting import Figure  # noqa: F401
from . import printing  # noqa: F401
from . import variable_names  # noqa: F401
from . import water_models  # noqa: F401
from . import zenodo  # noqa: F401
from .zenodo import Zenodo  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions

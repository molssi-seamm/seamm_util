# -*- coding: utf-8 -*-

"""Functions for handling MDL molfiles"""

import configargparse
import logging
import os.path
import seamm  # Due to handling of units, should be before util
import seamm_util
import seamm_util.molfile
import pprint
import re

obabel_exe = None

logger = logging.getLogger(__name__)


def from_seamm(structure):
    """Convert a SEAMM structure to SMILES"""
    # obabel play/ethanol.mol -osmi -xh

    # If we don't know where the obabel executable is, find it!
    global obabel_exe
    if obabel_exe is None:
        # Argument/config parsing
        parser = configargparse.ArgParser(
            auto_env_var_prefix='',
            default_config_files=[
                '/etc/seamm/openbabel.ini',
                '/etc/seamm/seamm.ini',
                '~/.seamm/openbabel.ini',
                '~/.seamm/seamm.ini',
            ]
        )

        parser.add_argument(
            '--seamm-configfile',
            is_config_file=True,
            default=None,
            help='a configuration file to override others'
        )

        # Options for OpenBabel
        parser.add_argument(
            '--openbabel-path',
            default='',
            help='the path to the OpenBabel executables'
        )

        o, unknown = parser.parse_known_args()

        obabel_exe = os.path.join(o.openbabel_path, 'obabel')

        seamm_util.check_executable(
            obabel_exe, key='--openbabel-path', parser=parser
        )

    # Continue on
    mol3 = seamm_util.molfile.from_seamm(structure)
    logger.debug('molfile:\n' + mol3)

    local = seamm.ExecLocal()
    result = local.run(
        cmd=[obabel_exe, '-imol', '-osmi', '-xh'], input_data=mol3
    )

    logger.debug('Result from obabel')
    logger.debug(pprint.pformat(result))

    if int(result['stderr'].split()[0]) == 0:
        raise RuntimeError(
            'There was an error creating the SMILES:\n' + result['stderr']
        )

    logger.debug('***SMILES from obabel')
    logger.debug(result['stdout'])

    pat3 = re.compile('H3\]')  # noqa: W605
    pat2 = re.compile('H2\]')  # noqa: W605
    pat1 = re.compile('(?P<c1>[^[])H\]')  # noqa: W605

    smiles = pat3.sub(']([H])([H])([H])', result['stdout'])
    smiles = pat2.sub(']([H])([H])', smiles)
    smiles = pat1.sub('\g<c1>]([H])', smiles)  # noqa: W605

    logger.debug(smiles)

    return smiles

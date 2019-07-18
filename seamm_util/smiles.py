# -*- coding: utf-8 -*-

"""Functions for handling MDL molfiles"""

import logging
import seamm  # Due to handling of units, should be before util
import seamm_util.molfile
import pprint
import re

logger = logging.getLogger(__name__)


def from_seamm(structure):
    """Convert a SEAMM structure to SMILES"""
    # obabel play/ethanol.mol -osmi -xh

    mol3 = seamm_util.molfile.from_seamm(structure)
    logger.debug('molfile:\n' + mol3)

    local = seamm.ExecLocal()
    result = local.run(
        cmd=['obabel', '-imol', '-osmi', '-xh'], input_data=mol3
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

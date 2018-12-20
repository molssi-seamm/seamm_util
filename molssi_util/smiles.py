# -*- coding: utf-8 -*-
"""Functions for handling MDL molfiles"""

import molssi_workflow
import logging
import molssi_util.molfile
import pprint
import re

logger = logging.getLogger(__name__)


def from_molssi(structure):
    """Convert a MolSSI structure to SMILES"""
    # obabel play/ethanol.mol -osmi -xh

    mol3 = molssi_util.molfile.from_molssi(structure)
    logger.debug('molfile:\n' + mol3)

    local = molssi_workflow.ExecLocal()
    result = local.run(cmd=['obabel', '-imol', '-osmi', '-xh'],
                       input_data=mol3)

    logger.debug('Result from obabel')
    logger.debug(pprint.pformat(result))

    if int(result['stderr'].split()[0]) == 0:
        raise RuntimeError('There was an error creating the SMILES:\n'
                           + result['stderr'])

    logger.debug('***SMILES from obabel')
    logger.debug(result['stdout'])

    pat3 = re.compile('H3\]')
    pat2 = re.compile('H2\]')
    pat1 = re.compile('(?P<c1>[^[])H\]')

    smiles = pat3.sub(']([H])([H])([H])', result['stdout'])
    smiles = pat2.sub(']([H])([H])', smiles)
    smiles = pat1.sub('\g<c1>]([H])', smiles)

    logger.debug(smiles)

    return smiles

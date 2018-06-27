#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge `exp_recsys` results containing information only for one fold into one
file.

     <script> <options> <infile_1> <infile_2> ...

Description
===========

Merge files generated by the experimental scripts by specifying fold number.
These files contain the information of results of each fold in the same
sequence of the cross-validation.

Options
=======

-o <OUTPUT>, --out <OUTPUT>
    specify <OUTPUT> file name. default=STDOUT
-q, --quiet
    set logging level to ERROR, no messages unless errors
-h, --help
    show this help message and exit
--version
    show program's version number and exit
"""

from __future__ import (
    print_function,
    division,
    absolute_import)
from six.moves import xrange

# =============================================================================
# Imports
# =============================================================================

import argparse
import logging
import sys
import json

import numpy as np

from kamrecsys.utils import json_decodable

# =============================================================================
# Metadata variables
# =============================================================================

__author__ = "Toshihiro Kamishima ( http://www.kamishima.net/ )"
__date__ = "2017-12-26"
__version__ = "2.0.0"
__copyright__ = "Copyright (c) 2017 Toshihiro Kamishima all rights reserved."
__license__ = "MIT License: http://www.opensource.org/licenses/mit-license.php"

# =============================================================================
# Public symbols
# =============================================================================

__all__ = []

# =============================================================================
# Constants
# =============================================================================

# =============================================================================
# Module variables
# =============================================================================

# =============================================================================
# Functions
# =============================================================================


def first_fold(fp):
    """
    Create information of a new fold to the existing experimental results

    Parameters
    ----------
    fp : file
        the first file to merge

    Returns
    -------
    cv_info : dict
        merged experimental results
    """

    # load json file of the target fold
    cv_info = json.load(fp, encoding='utf-8')

    # add mmake container of merged information
    cv_info['condition']['merged'] = True

    # get fold number
    fold = next(iter(cv_info['training']['results']))

    # copy computation environments for this fold
    this_environment = cv_info['environment'].copy()
    cv_info['environment']['environment_fold'] = {fold: this_environment}

    # close file
    fp.close()

    return cv_info


def rest_fold(fp, cv_info):
    """
    Add information of a new fold to the existing experimental results

    Parameters
    ----------
    fp : file
        the first file to merge
    cv_info : dict
        merged experimental results
    """

    # load json file of the target fold
    info = json.load(fp, encoding='utf-8')

    # get fold number
    fold = next(iter(info['training']['results']))

    # copy computation environments for this fold
    cv_info['environment']['environment_fold'][fold] = info['environment']

    # copy results
    cv_info['training']['results'][fold] = info['training']['results'][fold]
    cv_info['test']['results'][fold] = info['test']['results'][fold]
    cv_info['prediction']['event'][fold] = info['prediction']['event'][fold]
    cv_info['prediction']['true'][fold] = info['prediction']['true'][fold]
    cv_info['prediction']['predicted'][fold] = (
        info['prediction']['predicted'][fold])
    cv_info['prediction']['mask'][fold] = info['prediction']['mask'][fold]
    if 'event_feature' in cv_info['prediction']:
        for k in cv_info['prediction']['event_feature']:
            cv_info['prediction']['event_feature'][k][fold] = (
                info['prediction']['event_feature'][k][fold])

    # close file
    fp.close()


def do_task(opt):
    """
    Main task

    Parameters
    ----------
    opt : Options
        parsed command line options
    """

    # pre process #####

    # main process #####

    infile = opt.infile[0]
    logger.info("Processing \"" + infile.name + "\"")
    cv_info = first_fold(infile)

    for i in range(1, len(opt.infile)):
        infile = opt.infile[i]
        logger.info("Processing \"" + infile.name + "\"")
        rest_fold(infile, cv_info)

    # post process #####

    # output information
    cv_info['condition']['out_file'] = str(opt.outfile)
    json_decodable(cv_info)
    opt.outfile.write(json.dumps(cv_info))
    if opt.outfile is not sys.stdout:
        opt.outfile.close()


# =============================================================================
# Classes
# =============================================================================

# =============================================================================
# Main routine
# =============================================================================


def command_line_parser():
    """
    Parsing Command-Line Options

    Returns
    -------
    opt : argparse.Namespace
        Parsed command-line arguments
    """
    # import argparse
    # import sys

    # Initialization #####

    # command-line option parsing #####
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)

    # common options
    ap.add_argument('--version', action='version',
                    version='%(prog)s ' + __version__)

    apg = ap.add_mutually_exclusive_group()
    apg.set_defaults(verbose=True)
    apg.add_argument('--verbose', action='store_true')
    apg.add_argument('-q', '--quiet', action='store_false', dest='verbose')

    # basic file i/o
    ap.add_argument('-o', '--out', dest='outfile', default=sys.stdout,
                    type=argparse.FileType('w'))
    ap.add_argument('infile', nargs='+', metavar='INFILE',
                    type=argparse.FileType('r'))

    # parsing
    opt = ap.parse_args()

    # post-processing for command-line options

    # disable logging messages by changing logging level
    if opt.verbose:
        logger.setLevel(logging.INFO)

    return opt


def main():
    """ Main routine
    """
    # command-line arguments
    opt = command_line_parser()

    # do main task
    do_task(opt)


# top level -------------------------------------------------------------------
# init logging system
logger = logging.getLogger('exp_recsys')
logging.basicConfig(level=logging.INFO, format='[%(name)s: %(levelname)s'
                                               ' @ %(asctime)s] %(message)s')
logger.setLevel(logging.ERROR)

# Call main routine if this is invoked as a top-level script environment.
if __name__ == '__main__':
    main()

    sys.exit(0)

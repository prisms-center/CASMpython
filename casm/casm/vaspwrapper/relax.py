"""Defines the relax module methods"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import *

import json
import math
import os
import re
import six
import sys
import json
import shutil
import casm
from casm.vaspwrapper.vasp_calculator_base import VaspCalculatorBase
from casm.vasp import Relax as calculator

from casm import vasp, wrapper
from casm.misc import noindent
from casm.project import DirectoryStructure, ProjectSettings
from casm.vaspwrapper import VaspWrapperError, read_settings, write_settings
from casm.vaspwrapper.vasp_calculator_base import VaspCalculatorBase


class Relax(VaspCalculatorBase):
    """The Relax class contains functions for setting up, executing, and parsing a VASP relaxation.

    Attributes
    ----------
    selection : casm.project.Selection
        selection of configuration
    calctype : string
        calctype to setup and run the calculation
    auto : bool
    sort : bool

    Methods
    -------
    from_configuration_dir(configuration_dir='string', calctype='string', bool, bool)
        returns a instance of the Neb class instantited with a single configuration
    config_properties(config_data=dict/Pandas.DataFrame)
        return a dict of the properties required to setup a configuration
    pre_setup
        creates folder and makes POS files for each image
    setup
        sets up the input vasp files for the selection
    config_setup
        sets up the input vasp files for a single configuration
    get_vasp_input_files(config_data=dict/Pandas.DataFrame, settings=dict)
        returns filenames of a vasp calculation
    submit
        submit a job for each configuration
    run
        runs the calcutation on the selection
    report
        reports results for the selection
    run_cmd(configdir='string', calctype='string')
        return a string of command to run a single configuration
    finalize(config_data=dict/pandas_data, super_poscarfile='string')
        checks convergnce and write a properties file for the selection
    properties(calcdir='string', super_poscarfile='string', speciesfile='string')
        return a dict containing all the relaxed properties for a configuration

    Notes
    -----
    The Relax class contains functions for setting up, executing, and parsing a VASP relaxation.

    The relaxation creates the following directory structure:
    config/
        calctype.name/
            run.0/
            ....

    'run.i' directories are only created when ready.

    This automatically looks for VASP settings files using:
        casm.project.DirectoryStructure.settings_path_crawl

    """
    def __init__(self, selection, calctype=None, auto=True, sort=True):
        """Construct a VASP job object"""
        print("Construct a casm.vaspwrapper.Relax instance:")
        VaspCalculatorBase.__init__(self, selection, calctype, auto, sort)
        self.calculator = calculator

    def pre_setup(self):
        """Setus up folders and writes structure files"""
        args = "query -c " + self.selection.path + " --write-structure"
        self.selection.proj.capture(args)
        for index, config_data in self.selection.data.iterrows():
            os.makedirs(config_data["calcdir"], exist_ok=True)

    def config_setup(self, config_data):
        """ Setup initial relaxation run for a configuration

            Uses the following files from the most local .../settings/calctype.name directory:
                INCAR: VASP input settings
                KPOINTS: VASP kpoints settings
                POSCAR: reference for KPOINTS if KPOINTS mode is not A/AUTO/Automatic
                SPECIES: info for each species such as which POTCAR files to use, MAGMOM, GGA+U, etc.

            Uses the following files from the .../config_calcdir/00 directory:
                POSCAR: sample structure of the configuration to be relaxed

        """
        settings = self.read_settings(config_data["setfile"])
        super(Relax, self).config_setup(config_data)
        if settings["initial_deformation"] != None:
            deformation = self.get_deformation(settings)
            self.apply_deformation(deformation, config_data["calcdir"])

    def setup(self):
        """Setup initial relaxation run for the selection"""
        super(Relax, self).setup()

    def submit(self):
        """Submit a job for each configuration"""
        super(Relax, self).submit()

    def run(self):
        """Runs the calcutation on the selection"""
        super(Relax, self).run()

    def report(self):
        """Reports results for the selection"""
        super(Relax, self).report()

    @staticmethod
    def run_cmd(configdir, calctype):
        """Return a string of command to run a single configuration"""
        return "python -c \"import casm.vaspwrapper; obj = casm.vaspwrapper.Relax.from_configuration_dir('{0}', '{1}'); obj.run()\"\n".format(
            configdir, calctype)

    def finalize(self, config_data):
        """Checks convergnce and write a properties file for the selection"""
        super(Relax, self).finalize(config_data)
        sys.stdout.flush()

    @staticmethod
    def properties(calcdir, super_poscarfile=None, speciesfile=None):
        """Make properties output as a list of dict of each image properties"""
        output = super(Relax, Relax).properties(
            calcdir, super_poscarfile, speciesfile)
        return output

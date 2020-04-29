"""test_casm/test_vasp/test_omc.py"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *

# TODO: which imports are actually needed?
import unittest
import os
from os.path import join
import json

from casm import vasp
from casm.vasp import io
from casm.misc.contexts import working_dir, captured_output, print_stringIO

import test_casm
from test_casm.test_vasp import CasmVaspTestCase, cp_input

class TestCasmVaspReadOccupationMatrix(CasmVaspTestCase):

    def setUp(self):
        """Read test case data"""
        with open(join(self.classdir, 'test_cases.json'), 'r') as f:
            self.cases = json.load(f)["vasp"]["read_occupation_matrix"]            

    def test_run(self):
        """Test Outcar.read() for occupation matrices"""
        for case in self.cases:
            input_outcar = join(self.classdir, 'input_data', case['input_data'])
            test_outcar = io.Outcar(input_outcar)
            self.assertTrue(test_outcar.complete)
            for site_spin in case["expected_occupation_matrices"]:
                self.assertTrue(test_outcar.occupation_matrix[site_spin["basis_site"]][site_spin["spin_channel"]] == site_spin["occupation_matrix"])


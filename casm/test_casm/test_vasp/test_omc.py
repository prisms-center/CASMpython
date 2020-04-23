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
        outcar_file = join(self.classdir,'input_data/LiNiO2_final/OUTCAR') 
        self.test_outcar = io.Outcar(outcar_file)
        self.spin_up_occupation_matrix = [[ 0.9800, -0.0872, -0.0025, -0.0250, -0.0623],
                                          [-0.0872,  0.7954, -0.0026, -0.1304, -0.1255],
                                          [-0.0025, -0.0026,  0.9898,  0.0044,  0.0014],
                                          [-0.0250, -0.1304,  0.0044,  0.9457, -0.0872],
                                          [-0.0623, -0.1255,  0.0014, -0.0872,  0.9081]]
        self.spin_down_occupation_matrix = [[ 0.7552,  0.0430, -0.0173, -0.3123,  0.0373],
                                            [ 0.0430,  0.6204,  0.0090,  0.0414, -0.2627],
                                            [ -0.0173, 0.0090,  0.9865, -0.0156,  0.0100],
                                            [ -0.3123, 0.0414, -0.0156,  0.5727,  0.0430],
                                            [ 0.0373, -0.2627,  0.0100,  0.0430,  0.7982]] 
        
    def test_run(self):
        """ Test omc"""
        self.assertTrue(self.test_outcar.complete)
        self.assertTrue(self.test_outcar.occupation_matrix[1][0] == self.spin_up_occupation_matrix)
        self.assertTrue(self.test_outcar.occupation_matrix[1][1] == self.spin_down_occupation_matrix)


      




# what do I want to test?
    # read a config.json file
    # write occ mats to files

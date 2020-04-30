"""test_casm/test_vasp/test_omc.py"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *

# TODO: which imports are actually needed?
import unittest
import os
from os.path import join
import json
import numpy as np

from casm import vasp
from casm.vasp import io
from casm.vasp.io import OrbitalOccupation, write_occupations
from casm.misc.contexts import working_dir, captured_output, print_stringIO

import test_casm
from test_casm.test_vasp import CasmVaspTestCase, cp_input

class TestCasmOrbitalOccupationConstruction(CasmVaspTestCase):
    def test_run(self):
        """Test OrbitalOccupation construction for s,p,d,f orbtials,
            spin-polarized and non-spin-polarized cases,
            with input matrices given either as lists or numpy arrays
        """
        for input_matrix_type in ['list', 'array']:
            for l_quantum_number in range(4):
                test_matrix_a = np.identity(2*l_quantum_number+1)
                test_matrix_b = -np.identity(2*l_quantum_number+1)
                if input_matrix_type == 'list':
                    test_matrix_a = test_matrix_a.tolist()
                    test_matrix_b = test_matrix_b.tolist()
                for spin_polarized in [True, False]:
                    if spin_polarized:
                        test_occupation = OrbitalOccupation(test_matrix_a, test_matrix_b)
                    else:
                        test_occupation = OrbitalOccupation(test_matrix_a)
                self.assertTrue(test_occupation.l_quantum_number == l_quantum_number)
                self.assertTrue(test_occupation.spin_polarized == spin_polarized)
                self.assertTrue(np.array_equal(test_occupation.matrices[0], test_matrix_a))
                if spin_polarized:
                    self.assertTrue(len(test_occupation.matrices) == 2)
                    self.assertTrue(np.array_equal(test_occupation.matrices[1], test_matrix_b))
                else:
                    self.assertTrue(len(test_occupation.matrices) == 1)


class TestCasmVaspReadOccupationMatrix(CasmVaspTestCase):

    def setUp(self):
        """Read test case data"""
        with open(join(self.classdir, 'test_cases.json'), 'r') as f:
            self.cases = json.load(f)['vasp']['read_write_occupation_matrix']

    def test_run(self):
        """Test Outcar.read() for occupation matrices"""
        for case in self.cases:
            input_outcar = join(self.classdir, 'input_data', case['input_data'], 'OUTCAR')
            test_outcar = io.Outcar(input_outcar)
            self.assertTrue(test_outcar.complete)
            for site in case['site_occupation_matrices']:
                for spin_channel, occupation_matrix in enumerate(site['occupation_matrices']):
                    print("site noomber "+str(site["site_index"]))
                    print(occupation_matrix)
                    print(test_outcar.orbital_occupations[site["site_index"]].matrices[spin_channel].tolist())
                    self.assertTrue(test_outcar.orbital_occupations[site['site_index']].matrices[spin_channel].tolist() == occupation_matrix)


class TestCasmVaspWriteOccupationMatrix(CasmVaspTestCase):

    def setUp(self):
        """Read test case data"""
        with open(join(self.classdir, 'test_cases.json'), 'r') as f:
            self.cases = json.load(f)['vasp']['read_write_occupation_matrix']

    def test_run(self):
        """Test write_occupations function"""
        for case in self.cases:
            occupations = {}
            for site in case['site_occupation_matrices']:
                occupations[site['site_index']] = OrbitalOccupation(*tuple(site['occupation_matrices']))
            output_filename = join(self.classdir, 'output_data', case['output_data'],'OCCMATRIX')
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            write_occupations(output_filename, occupations)
            with open(output_filename, 'r') as output:
                with open(join(self.classdir, 'input_data', case['input_data'], 'OCCMATRIX'), 'r') as expected_output:
                    self.assertTrue(output.read() == expected_output.read())


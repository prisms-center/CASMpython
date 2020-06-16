"""test_casm/test_matrix/test_matrix.py"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *

import unittest
import os
from os.path import join
import json

import numpy as np
from casm.misc import matrix

import test_casm
from test_casm.test_matrix import CasmMatrixTestCase

class TestCasmMatrixCanonicalUnrollIndexList(CasmMatrixTestCase):

    def setUp(self):
        self.expected_indices = {}
        self.expected_indices[1] = [(0,0)]
        self.expected_indices[2] = [(0,0),(1,1),(0,1)]
        self.expected_indices[3] = [(0,0),(1,1),(2,2),(1,2),(0,2),(0,1)]
        self.expected_indices[4] = [(0,0),(1,1),(2,2),(3,3),(2,3),(1,3),(0,3),(0,2),(0,1),(1,2)]
        self.expected_indices[5] = [(0,0),(1,1),(2,2),(3,3),(4,4),(3,4),(2,4),(1,4),(0,4),(0,3),(0,2),(0,1),(1,2),(2,3),(1,3)]

    def test_run(self):
        for dim in self.expected_indices.keys():
            self.assertTrue(matrix.canonical_unroll_index_list(dim) == self.expected_indices[dim])


class TestCasmMatrixReductionMatrix(CasmMatrixTestCase):

    def setUp(self):
        self.expected_matrices = {}
        self.expected_matrices[5] = [ [ 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 1/np.sqrt(2), 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 1/np.sqrt(2), 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0 ],
                                      [ 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0] ]

    def test_run(self):
        for dim in self.expected_matrices.keys():
            self.assertTrue(matrix.reduction_matrix(dim).tolist() == self.expected_matrices[dim])


class TestCasmMatrixUnrollRerollSymmetricMatrix(CasmMatrixTestCase):

    def setUp(self):
        self.test_vectors = []
        self.test_matrices = []
        self.test_vectors.append(range(6))
        self.test_matrices.append( [ [ 0, 5/np.sqrt(2), 4/np.sqrt(2) ],
                                     [ 5/np.sqrt(2), 1, 3/np.sqrt(2) ],
                                     [ 4/np.sqrt(2), 3/np.sqrt(2), 2 ] ] )
        self.test_vectors.append(range(15))
        self.test_matrices.append( [ [ 0, 11/np.sqrt(2), 10/np.sqrt(2), 9/np.sqrt(2), 8/np.sqrt(2) ],
                                     [ 11/np.sqrt(2), 1, 12/np.sqrt(2), 14/np.sqrt(2), 7/np.sqrt(2) ],
                                     [ 10/np.sqrt(2), 12/np.sqrt(2), 2, 13/np.sqrt(2), 6/np.sqrt(2) ],
                                     [ 9/np.sqrt(2), 14/np.sqrt(2), 13/np.sqrt(2), 3, 5/np.sqrt(2) ],
                                     [ 8/np.sqrt(2), 7/np.sqrt(2), 6/np.sqrt(2), 5/np.sqrt(2), 4 ] ] )

    def test_run(self):
        for i, vec in enumerate(self.test_vectors):
            mat = self.test_matrices[i]
            self.assertTrue(np.allclose(matrix.unroll_symmetric_matrix(mat), np.array(vec)))
            self.assertTrue(np.allclose(matrix.reroll_symmetric_matrix(vec), np.array(mat)))


class TestCasmMatrixIsZero(CasmMatrixTestCase):

    def setUp(self):
        pass

    def test_run(self):
        self.assertTrue(matrix.is_zero(np.zeros((5,5))))
        self.assertTrue(matrix.is_zero(1e-09*np.ones((3,3)), tol=1e-08))
        self.assertFalse(matrix.is_zero(1e-07*np.ones((3,3)), tol=1e-08))
        self.assertFalse(matrix.is_zero(np.ones((1,15))))

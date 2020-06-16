"""test_casm/test_matrix/misc.py"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *

import os
import unittest
import warnings

from distutils.spawn import find_executable
from os.path import join

import test_casm

def casm_matrix_setup(self):
    """Implements common setup for casm.matrix tests
      - check for 'skip' or 'skip_MyTestCase' files

    Notes:
        Standalone implementation to allow easier use by subpackages
    """

    # First run common setup for 'casm'
    test_casm.casm_setup(self)

class CasmMatrixTestCase(unittest.TestCase):
    """test_casm.test_matrix base unittest class"""

    @classmethod
    def setUpClass(cls):
        """On inherited classes, run our `setUp` method"""
        if cls is not CasmMatrixTestCase and cls.setUp is not CasmMatrixTestCase.setUp:
            orig_setUp = cls.setUp
            def setUpOverride(self, *args, **kwargs):
                CasmMatrixTestCase.setUp(self)
                return orig_setUp(self, *args, **kwargs)
            cls.setUp = setUpOverride

    def setUp(self):
        """Common Setup:
          - check for 'skip' or 'skip_MyTestCase' files
        """
        casm_matrix_setup(self)

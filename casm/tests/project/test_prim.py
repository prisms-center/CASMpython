import os
import pytest
import numpy as np

import casm.api
import casm.project


def test_prim(initialized_ZrO_project):
    """Test Prim"""
    proj = initialized_ZrO_project
    prim = proj.prim

    assert prim.proj is proj
    assert proj.prim is prim

    expected_lattice_matrix = np.array([[3.23398686, -1.61699343, -0.],
                                        [0., 2.80071477, 0.],
                                        [0., 0., 5.16867834]])
    assert np.allclose(prim.lattice_matrix, expected_lattice_matrix)
    assert prim.lattice_parameters['a'] == pytest.approx(3.23398686)
    assert prim.lattice_parameters['b'] == pytest.approx(3.23398686)
    assert prim.lattice_parameters['c'] == pytest.approx(5.16867834)
    assert prim.lattice_parameters['alpha'] == pytest.approx(90.)
    assert prim.lattice_parameters['beta'] == pytest.approx(90.)
    assert prim.lattice_parameters['gamma'] == pytest.approx(120.)

    assert prim.coordinate_mode == 'Fractional'
    assert prim.lattice_symmetry_s == 'D6h'
    assert prim.lattice_symmetry_hm == '6/mmm'
    assert prim.lattice_system == 'hexagonal'
    assert prim.crystal_symmetry_s == 'D6h'
    assert prim.crystal_symmetry_hm == '6/mmm'
    assert prim.crystal_system == 'hexagonal'
    assert prim.crystal_family == 'hexagonal'
    assert prim.space_group_number == '191:194'

    # TODO: update prim composition info
    # assert prim.components == ['Zr', 'Va', 'O']
    # assert prim.elements == ['Zr', 'Va', 'O']
    # assert prim.n_independent_compositions == 1
    # assert prim.degrees_of_freedom == ['occupation']

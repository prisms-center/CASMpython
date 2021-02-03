import json
import numpy as np
import pytest

import casm.vasp.io


def test_POSCAR_init_from_POSCAR(shared_datadir):

    # construct casm.vasp.io.Poscar from POSCAR file
    poscar_file = shared_datadir / "NaxNiO2/SCEL1_1_1_1_0_0_0/1/POS"
    structure = casm.vasp.io.Poscar(poscar_file)

    # check constructed values
    expected_lattice = np.array([[2.97587164, 0.00000000, 0.00000000],
                                 [1.48793582, 2.57718044, 0.00000000],
                                 [1.48793582, 0.85906015, 5.25081268]])
    expected_coord_mode = 'Direct'
    expected_scaling = 1.0
    expected_type_atoms = ['Na', 'Ni', 'O']
    expected_num_atoms = [1, 1, 2]
    expected_site_cart = False
    expected_sites = [
        np.array([0.00000000, 0.00000000, 0.00000000]),
        np.array([0.50000000, 0.50000000, 0.50000000]),
        np.array([0.76890441, 0.76890441, 0.69328678]),
        np.array([0.23109559, 0.23109559, 0.30671322])
    ]

    assert np.allclose(structure.lattice(), expected_lattice)
    assert structure.coord_mode == expected_coord_mode
    assert structure.scaling == expected_scaling
    assert structure.type_atoms == expected_type_atoms
    assert structure.num_atoms == expected_num_atoms
    for i, site in enumerate(structure.basis):
        assert site.cart == expected_site_cart
        assert np.allclose(site.position, expected_sites[i])


def test_POSCAR_init_from_CASM_structure(shared_datadir):

    # construct casm.vasp.io.Poscar from CASM structure.json file
    # -- reading method is determined by checking for .json suffix

    structure_file = shared_datadir / "NaxNiO2/SCEL1_1_1_1_0_0_0/1/structure.json"
    structure = casm.vasp.io.Poscar(structure_file)

    expected_lattice = np.array(
        [[2.975871643531, 0.000000000000, 0.000000000000],
         [1.487935821766, 2.577180437492, 0.000000000000],
         [1.487935821766, 0.859060145831, 5.250812683906]])
    expected_coord_mode = 'Cartesian'
    expected_scaling = 1.0
    expected_type_atoms = ['Na', 'Ni', 'O']
    expected_num_atoms = [1, 1, 2]
    expected_site_cart = True
    expected_sites = [
        np.array([0.000000000000, 0.000000000000, 0.000000000000]),
        np.array([2.975871643531, 1.718120291662, 2.625406341953]),
        np.array([4.463807465297, 2.577180437492, 3.640319021752]),
        np.array([1.487935821766, 0.859060145831, 1.610493662154])
    ]

    assert np.allclose(structure.lattice(), expected_lattice)
    assert structure.coord_mode == expected_coord_mode
    assert structure.scaling == expected_scaling
    assert structure.type_atoms == expected_type_atoms
    assert structure.num_atoms == expected_num_atoms
    for i, site in enumerate(structure.basis):
        assert site.cart == expected_site_cart
        assert np.allclose(site.position, expected_sites[i])

import json
import os
import pytest
import random

import casm.project


def test_read_basis(ZrO_project_with_basis_functions):
    proj = ZrO_project_with_basis_functions
    basis_file = proj.dir.basis(proj.settings.default_clex)

    with open(basis_file, 'r') as f:
        basis_json = json.load(f)

    assert True


def test_write_eci(ZrO_project_with_basis_functions):
    proj = ZrO_project_with_basis_functions
    clex = proj.settings.default_clex
    basis_file = proj.dir.basis(clex)
    eci_file = proj.dir.eci(clex)

    # eci list: list of (basis function index, coefficient value)
    eci = [(0, random.random()), (1, 0.)]
    eci_by_function_index = {pair[0]:pair[1] for pair in eci}

    assert os.path.exists(eci_file) == False
    casm.project.write_eci(proj, eci, clex=proj.settings.default_clex)

    assert os.path.exists(eci_file) == True
    with open(eci_file, 'r') as f:
        eci_json = json.load(f)

    assert eci_json["orbits"][0]["cluster_functions"][0]["eci"] == pytest.approx(eci[0][1])
    assert eci_json["orbits"][1]["cluster_functions"][0]["eci"] == pytest.approx(0.)
    for orbit in eci_json["orbits"]:
        for function in orbit["cluster_functions"]:
            linear_function_index = function["linear_function_index"]
            if linear_function_index not in eci_by_function_index:
                assert "eci" not in function
            else:
                value = eci_by_function_index[linear_function_index]
                assert function["eci"] == pytest.approx(value)

    # TODO: separate test_use_eci
    sel = casm.project.Selection(proj, path="ALL")
    sel.query(['corr'])
    assert sel.data.shape == (336, 76)
    sel.query(['clex(formation_energy)'])
    assert sel.data.shape == (336, 77)


def test_read_basis(FCC_ternary_project_with_basis_functions):
    proj = FCC_ternary_project_with_basis_functions
    basis_file = proj.dir.basis(proj.settings.default_clex)

    with open(basis_file, 'r') as f:
        basis_json = json.load(f)

    assert True


def test_write_eci(FCC_ternary_project_with_basis_functions):
    proj = FCC_ternary_project_with_basis_functions
    clex = proj.settings.default_clex
    basis_file = proj.dir.basis(clex)
    eci_file = proj.dir.eci(clex)

    # eci list: list of (basis function index, coefficient value)
    eci = [(0, random.random()), (1, 0.), (7, random.random()) ]
    eci_by_function_index = {pair[0]:pair[1] for pair in eci}

    assert os.path.exists(eci_file) == False
    casm.project.write_eci(proj, eci, clex=proj.settings.default_clex)

    assert os.path.exists(eci_file) == True
    with open(eci_file, 'r') as f:
        eci_json = json.load(f)

    assert eci_json["orbits"][0]["cluster_functions"][0]["eci"] == pytest.approx(eci[0][1])
    assert eci_json["orbits"][1]["cluster_functions"][0]["eci"] == pytest.approx(0.)
    assert eci_json["orbits"][3]["cluster_functions"][1]["eci"] == pytest.approx(eci[2][1])
    for orbit in eci_json["orbits"]:
        for function in orbit["cluster_functions"]:
            linear_function_index = function["linear_function_index"]
            if linear_function_index not in eci_by_function_index:
                assert "eci" not in function
            else:
                value = eci_by_function_index[linear_function_index]
                assert function["eci"] == pytest.approx(value)

    # TODO: separate test_use_eci
    sel = casm.project.Selection(proj, path="ALL")
    sel.query(['corr'])
    assert sel.data.shape == (126, 77)
    sel.query(['clex(formation_energy)'])
    assert sel.data.shape == (126, 78)

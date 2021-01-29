import json
import os
import pytest
import random

import casm.project


def test_read_basis(ZrO_project_with_basis_functions):
    proj = ZrO_project_with_basis_functions
    basis_file = proj.dir.basis(proj.settings.default_clex)
    #print(basis_file)

    with open(basis_file, 'r') as f:
        basis_json = json.load(f)
    #print(basis_json)

    assert True


def test_write_eci(ZrO_project_with_basis_functions):
    proj = ZrO_project_with_basis_functions
    clex = proj.settings.default_clex
    basis_file = proj.dir.basis(clex)
    eci_file = proj.dir.eci(clex)

    #print(basis_file)
    #print(eci_file)

    # eci list: list of (basis function index, coefficient value)
    eci = [(0, random.random()), (1, 0.)]

    assert os.path.exists(eci_file) == False
    casm.project.write_eci(proj, eci, clex=proj.settings.default_clex)

    assert os.path.exists(eci_file) == True
    with open(eci_file, 'r') as f:
        eci_json = json.load(f)

    assert eci_json["orbits"][0]["eci"] == pytest.approx(eci[0][1])
    assert eci_json["orbits"][1]["eci"] == pytest.approx(0.)
    for i in range(len(eci_json["orbits"])):
        if i > 1:
            assert "eci" not in eci_json["orbits"][i]

    # TODO:
    # sel = casm.project.Selection(proj, path="ALL")
    # sel.query(['clex("formation_energy")'])
    # print(sel.data)

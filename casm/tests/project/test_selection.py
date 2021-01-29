import os
import pytest

import casm.project


def test_selection_init_config(ZrO_project):
    proj = ZrO_project
    sel = casm.project.Selection(proj)
    assert sel.proj is proj
    assert sel.path == "MASTER"
    assert sel.all == True
    assert sel.type == "config"


def test_selection_init_scel(ZrO_project):
    proj = ZrO_project
    sel = casm.project.Selection(proj, type="scel")
    assert sel.proj is proj
    assert sel.path == "MASTER"
    assert sel.all == True
    assert sel.type == "scel"


def test_selection_init_scel_all(ZrO_project):
    proj = ZrO_project
    sel = casm.project.Selection(proj, path="ALL", type="scel")
    assert sel.proj is proj
    assert sel.path == "ALL"
    assert sel.all == True
    assert sel.type == "scel"


def test_selection_scel(ZrO_project_ScelEnum_max4):
    """Test 'scel' MASTER selection immediately after enumeration"""
    proj = ZrO_project_ScelEnum_max4
    sel = casm.project.Selection(proj, type="scel")

    assert sel.proj is proj
    assert sel.path == "MASTER"
    assert sel.all == True
    assert sel.type == "scel"

    n_total = 20
    assert sel.data.shape == (n_total, 2)
    assert sel.data.columns[0] == 'name'
    assert sel.data.columns[1] == 'selected'
    assert sel.data.dtypes[0] == 'object'
    assert sel.data.dtypes[1] == 'bool'
    assert list(sel.data['selected']) == [True] * n_total


def test_selection_config(ZrO_project_ConfigEnumAllOccupations_max4):
    """Test 'scel' MASTER selection immediately after enumeration"""
    proj = ZrO_project_ConfigEnumAllOccupations_max4
    sel = casm.project.Selection(proj, type="config")

    assert sel.proj is proj
    assert sel.path == "MASTER"
    assert sel.all == True
    assert sel.type == "config"

    n_total = 336
    assert sel.data.shape == (n_total, 2)
    assert sel.data.columns[0] == 'name'
    assert sel.data.columns[1] == 'selected'
    assert sel.data.dtypes[0] == 'object'
    assert sel.data.dtypes[1] == 'bool'
    assert list(sel.data['selected']) == [True] * n_total


def test_selection_json(ZrO_project_json_selection):
    proj, filename = ZrO_project_json_selection
    sel = casm.project.Selection(proj, filename, type="config")

    assert sel.proj is proj
    assert sel.path == filename
    assert sel.all == True
    assert sel.type == "config"

    n_total = 336
    assert sel.data.shape == (n_total, 2)
    assert sel.data.columns[0] == 'alias_or_name'
    assert sel.data.columns[1] == 'selected'
    assert sel.data.dtypes[0] == 'object'
    assert sel.data.dtypes[1] == 'bool'
    assert list(sel.data['selected']) == [True] * n_total


def test_selection_query(ZrO_selection_ConfigEnumAllOccupations_max4):
    sel = ZrO_selection_ConfigEnumAllOccupations_max4
    columns = ["comp_n", "scel_size"]
    sel.query(columns)

    n_total = 336
    assert sel.data.shape == (n_total, 6)
    assert sel.data.columns.tolist() == [
        'name', 'selected', 'comp_n(Zr)', 'comp_n(Va)', 'comp_n(O)',
        'scel_size'
    ]
    assert sel.data.dtypes.tolist() == [
        'object', 'bool', 'float64', 'float64', 'float64', 'int64'
    ]


def test_selection_saveas(ZrO_selection_ConfigEnumAllOccupations_max4):
    sel = ZrO_selection_ConfigEnumAllOccupations_max4
    proj = sel.proj
    filename = os.path.join(proj.path, "selection")

    assert os.path.exists(filename) == False
    sel.saveas(filename)
    assert os.path.exists(filename) == True

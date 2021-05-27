import os
import pytest

import casm.info

# Tests of basic execution only, not each property


def test_neighbor_list_info_desc():
    info_desc = casm.info.neighbor_list_info_desc()
    assert isinstance(info_desc, str)
    assert len(info_desc)


def test_neighbor_list_info_no_project(ZrO_prim_dict):
    neighbor_list_properties = ["prim_neighbor_list"]
    unitcells = [[0, 0, 0], [1, 0, 0], [0, 0, 1]]
    neighbor_list_info = casm.info.get_neighbor_list_info(
        prim=ZrO_prim_dict,
        unitcells=unitcells,
        properties=neighbor_list_properties)
    assert "prim_neighbor_list" in neighbor_list_info


def test_neighbor_list_info_no_prim_failure(ZrO_prim_dict):
    with pytest.raises(Exception) as excinfo:
        prim_info = casm.info.get_neighbor_list_info(
            prim={}, properties=["prim_neighbor_list"])
    err_msg = 'Error getting neighbor_list info'
    assert err_msg in str(excinfo.value)


def test_neighbor_list_info_with_project(ZrO_project):
    neighbor_list_properties = ["prim_neighbor_list"]
    unitcells = [[0, 0, 0], [1, 0, 0], [0, 0, 1]]
    neighbor_list_info = casm.info.get_neighbor_list_info(
        root=ZrO_project.path,
        unitcells=unitcells,
        properties=neighbor_list_properties)
    assert "prim_neighbor_list" in neighbor_list_info

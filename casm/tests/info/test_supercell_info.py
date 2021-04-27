import os
import pytest

import casm.info

# Tests of basic execution only, not each property


def test_supercell_info_desc():
    info_desc = casm.info.supercell_info_desc()
    assert isinstance(info_desc, str)
    assert len(info_desc)


def test_supercell_info_no_project(ZrO_prim_dict):
    supercell_properties = ["supercell_size"]
    transformation_matrix_to_super = [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
    supercell_info = casm.info.get_supercell_info(
        prim=ZrO_prim_dict,
        transformation_matrix_to_super=transformation_matrix_to_super,
        properties=supercell_properties)
    assert supercell_info["supercell_size"] == 8


def test_supercell_info_no_prim_failure(ZrO_prim_dict):
    with pytest.raises(Exception) as excinfo:
        prim_info = casm.info.get_supercell_info(prim={},
                                                 properties=["supercell_size"])
    err_msg = 'Error getting supercell info'
    assert err_msg in str(excinfo.value)


def test_supercell_info_with_project(ZrO_project):
    supercell_properties = ["supercell_size"]
    transformation_matrix_to_super = [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
    supercell_info = casm.info.get_supercell_info(
        root=ZrO_project.path,
        transformation_matrix_to_super=transformation_matrix_to_super,
        properties=supercell_properties)
    assert supercell_info["supercell_size"] == 8

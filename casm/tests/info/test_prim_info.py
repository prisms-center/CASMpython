import os
import pytest

import casm.info

# Tests of basic execution only, not each property


def test_prim_info_desc():
    info_desc = casm.info.prim_info_desc()
    assert isinstance(info_desc, str)
    assert len(info_desc)


def test_prim_info_no_project(ZrO_prim_dict):
    prim_properties = ["factor_group_size"]
    prim_info = casm.info.get_prim_info(prim=ZrO_prim_dict,
                                        properties=prim_properties)
    assert prim_info["factor_group_size"] == 24


def test_prim_info_no_prim_failure(ZrO_prim_dict):
    with pytest.raises(Exception) as excinfo:
        prim_info = casm.info.get_prim_info(prim={},
                                            properties=["factor_group_size"])
    err_msg = 'Error getting prim info'
    assert err_msg in str(excinfo.value)


def test_prim_info_with_project(ZrO_project):
    prim_properties = ["factor_group_size"]
    prim_info = casm.info.get_prim_info(root=ZrO_project.path,
                                        properties=prim_properties)
    assert prim_info["factor_group_size"] == 24

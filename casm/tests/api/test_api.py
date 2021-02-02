import ctypes
import json
import os
import pytest

import casm.api


def test_API_init():
    # this loads libcasm and libccasm one and only one time
    api = casm.api.API()
    assert len(api.__dict__) == 0
    assert isinstance(api._API__api.lib_casm, ctypes.CDLL)
    assert isinstance(api._API__api.lib_ccasm, ctypes.CDLL)
    assert isinstance(casm.api.API._API__api.lib_casm, ctypes.CDLL)
    assert isinstance(casm.api.API._API__api.lib_ccasm, ctypes.CDLL)


def test_command_list():
    api = casm.api.API()
    command_list = json.loads(api.command_list())
    assert "init" in command_list


def test_capture_init(clean_ZrO_dir):
    project_path, prim_path = clean_ZrO_dir
    args = "init --path=" + str(project_path) + " --prim=" + str(prim_path)
    stdout, stderr, returncode = casm.api.casm_capture(args, root=None)
    if returncode != 0:
        print(stdout)
        print(stderr)
    assert returncode == 0
    for filename in [
            ".casm", "basis_sets", "cluster_expansions", "symmetry",
            "training_data"
    ]:
        assert os.path.exists(project_path.join(filename))

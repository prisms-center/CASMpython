import json
import os
import pytest
import shutil

import casm.api
import casm.project


def check(stdout, stderr, returncode):
    """Helper, to display output if commands fail"""
    if returncode != 0:
        print(stdout)
        print(stderr)
    assert returncode == 0


@pytest.fixture
def ZrO_prim_dict(shared_datadir):
    with open(shared_datadir / "ZrO_prim.json") as f:
        return json.load(f)


@pytest.fixture
def clean_ZrO_dir(shared_datadir, tmpdir):
    """Return (project_path, prim_path) tuple for a clean ZrO project directory.

    Returns
    -------
    (project_path, prim_path): Both paths are of type py.path.local
    """
    prim_path = tmpdir.join("prim.json")
    shutil.copyfile(shared_datadir / "ZrO_prim.json", prim_path)
    return (tmpdir, prim_path)


@pytest.fixture
def initialized_ZrO_project(clean_ZrO_dir):
    """Return casm.Project  for a ZrO project that has been initialized."""
    project_path, prim_path = clean_ZrO_dir
    args = "init --path=" + str(project_path) + " --prim=" + str(prim_path)
    check(*casm.api.casm_capture(args, root=None))
    proj = casm.project.Project(project_path, verbose=False)
    for filename in [
            ".casm", "basis_sets", "cluster_expansions", "symmetry",
            "training_data"
    ]:
        assert os.path.exists(os.path.join(proj.path, filename))
    return proj


@pytest.fixture
def ZrO_project_calc_composition_axes(initialized_ZrO_project):
    """Return a casm.Project for a ZrO project that has standard composition axes calculated."""
    proj = initialized_ZrO_project
    check(*proj.capture("composition --calc"))
    return proj


@pytest.fixture
def ZrO_project(clean_ZrO_dir):
    """Return a casm.Project for a ZrO project, initialized and composition axes selected."""
    project_path, prim_path = clean_ZrO_dir
    return casm.project.Project.init(root=project_path,
                                     prim_path=prim_path,
                                     verbose=False)

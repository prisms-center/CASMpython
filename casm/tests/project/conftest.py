import os
import pytest
import shutil

import casm.api


def check(stdout, stderr, returncode):
    """Helper, to display output if commands fail"""
    if returncode != 0:
        print(stdout)
        print(stderr)
    assert returncode == 0


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


@pytest.fixture
def ZrO_project_ScelEnum_max4(ZrO_project):
    """Return a casm.Project with supercells up to volume 4."""
    proj = ZrO_project
    check(*proj.capture("enum -m ScelEnum --max 4"))
    check(*proj.capture("select -t scel --set-on"))
    return proj


@pytest.fixture
def ZrO_project_ConfigEnumAllOccupations_max4(ZrO_project_ScelEnum_max4):
    """Return a casm.Project with configurations up to volume 4."""
    proj = ZrO_project_ScelEnum_max4
    check(*proj.capture("enum -m ConfigEnumAllOccupations --all"))
    check(*proj.capture("select --set-on"))
    return proj


@pytest.fixture
def ZrO_project_json_selection(ZrO_project_ConfigEnumAllOccupations_max4):
    """Return (casm.Project, filename) for a ZrO project with configurations up to volume 4 and a JSON selection file"""
    proj = ZrO_project_ConfigEnumAllOccupations_max4
    filename = os.path.join(proj.path, "selection.json")
    check(*proj.capture("select --set-on -o " + filename))
    return (proj, filename)


@pytest.fixture
def ZrO_selection_ConfigEnumAllOccupations_max4(
        ZrO_project_ConfigEnumAllOccupations_max4):
    proj = ZrO_project_ConfigEnumAllOccupations_max4
    sel = casm.project.Selection(proj, type="config")
    return sel


@pytest.fixture
def ZrO_project_with_basis_functions(ZrO_project_ConfigEnumAllOccupations_max4,
                                     shared_datadir):
    """Return a casm.Project for a ZrO project with basis functions."""
    proj = ZrO_project_ConfigEnumAllOccupations_max4
    bspecs_path = os.path.join(proj.path, "basis_sets", "bset.default",
                               "bspecs.json")
    shutil.copyfile(shared_datadir / "ZrO_bspecs.json", bspecs_path)
    check(*proj.capture("bset -uf"))
    return proj

@pytest.fixture
def FCC_ternary_project_with_basis_functions(shared_datadir, tmpdir):
    """Return a casm.Project for a FCC_ternary project with basis functions."""
    project_path = tmpdir
    prim_path = project_path.join("prim.json")
    shutil.copyfile(shared_datadir / "FCC_ternary_prim.json", prim_path)

    args = "init --path=" + str(project_path) + " --prim=" + str(prim_path)
    check(*casm.api.casm_capture(args, root=None))
    proj = casm.project.Project(project_path, verbose=False)
    check(*proj.capture("enum -m ConfigEnumAllOccupations --max 4"))

    bspecs_path = os.path.join(proj.path, "basis_sets", "bset.default",
                               "bspecs.json")
    shutil.copyfile(shared_datadir / "FCC_ternary_bspecs.json", bspecs_path)
    check(*proj.capture("bset -uf"))
    return proj

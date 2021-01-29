import shutil
import pytest


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

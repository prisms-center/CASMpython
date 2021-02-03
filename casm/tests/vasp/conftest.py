import os
import shutil
import pytest

# Note on VASP configuration (work in progress):
# - Set CASM_VASP_POTCAR_DIR (no default) to enable the `potcar_dir` fixture.
# - Set CASM_VASP_CMD (no default) to enable the `vasp_cmd` fixture.


@pytest.fixture
def potcar_dir():
    """ Return path to directory containing VASP POTCARs """
    dir = os.environ.get('CASM_VASP_POTCAR_DIR')
    if dir is None:
        pytest.skip(
            "vasp potcars not found (configure with CASM_VASP_POTCAR_DIR)")
    return dir


@pytest.fixture
def vasp_cmd():
    """ Return vasp execution command """
    cmd = os.environ.get('CASM_VASP_CMD')
    if cmd is None or shutil.which(cmd) is None:
        pytest.skip("vasp executable not found (configure with CASM_VASP_CMD)")
    return shutil.which(cmd)


@pytest.fixture
def ZrO_vasp_rundir(shared_datadir, potcar_dir, tmpdir):
    """ Return a prepared VASP calculation directory """
    rundir = tmpdir / "run"

    # cp INCAR, KPOINTS, POSCAR
    datadir = str(shared_datadir / "ZrO/SCEL1_1_1_1_0_0_0/2")
    shutil.copytree(datadir, rundir)

    # create POTCAR
    potcars = ["PAW_PBE/Zr_sv/POTCAR", "PAW_PBE/O_s/POTCAR"]
    with open(os.path.join(rundir, "POTCAR"), 'w') as file:
        for name in potcars:
            with open(os.path.join(potcar_dir, name)) as potcar:
                file.write(potcar.read())

    return rundir


@pytest.fixture
def orbital_occupation_case_1(shared_datadir):
    """ For LiNiO2/SCEL1_1_1_1_0_0_0/0 """
    outcar_file = str(shared_datadir / "LiNiO2/SCEL1_1_1_1_0_0_0/0")
    expected_site_occupation_matrices = [{
        "site_index":
        1,
        "occupation_matrices": [[[0.9800, -0.0872, -0.0025, -0.0251, -0.0624],
                                 [-0.0872, 0.7953, -0.0026, -0.1305, -0.1255],
                                 [-0.0025, -0.0026, 0.9898, 0.0044, 0.0014],
                                 [-0.0251, -0.1305, 0.0044, 0.9457, -0.0872],
                                 [-0.0624, -0.1255, 0.0014, -0.0872, 0.9081]],
                                [[0.7553, 0.0430, -0.0170, -0.3122, 0.0371],
                                 [0.0430, 0.6205, 0.0088, 0.0417, -0.2627],
                                 [-0.0170, 0.0088, 0.9866, -0.0153, 0.0098],
                                 [-0.3122, 0.0417, -0.0153, 0.5725, 0.0430],
                                 [0.0371, -0.2627, 0.0098, 0.0430, 0.7981]]]
    }]
    return (outcar_file, expected_site_occupation_matrices)


@pytest.fixture
def orbital_occupation_case_2(shared_datadir):
    """ For LiNiO2/SCEL2_2_1_1_0_0_0/0 """
    outcar_file = str(shared_datadir / "LiNiO2/SCEL2_2_1_1_0_0_0/0")
    expected_site_occupation_matrices = [{
        "site_index":
        2,
        "occupation_matrices": [[[0.8646, 0.0111, 0.0005, -0.1728, -0.0191],
                                 [0.0111, 1.0228, 0.0027, 0.0222, 0.0298],
                                 [0.0005, 0.0027, 0.9868, -0.0006, -0.0005],
                                 [-0.1728, 0.0222, -0.0006, 0.7429, -0.0217],
                                 [-0.0191, 0.0298, -0.0005, -0.0217, 1.0107]],
                                [[0.8048, 0.0439, 0.0000, -0.2407, 0.0033],
                                 [0.0439, 0.5352, -0.0092, -0.0054, -0.3295],
                                 [0.0000, -0.0092, 0.9854, -0.0024, -0.0108],
                                 [-0.2407, -0.0054, -0.0024, 0.6539, -0.0426],
                                 [0.0033, -0.3295, -0.0108, -0.0426, 0.7465]]]
    }, {
        "site_index":
        3,
        "occupation_matrices": [[[0.9907, 0.0687, 0.0007, -0.0162, 0.0537],
                                 [0.0687, 0.8319, -0.0008, 0.1323, -0.1268],
                                 [0.0007, -0.0008, 0.9868, -0.0027, -0.0002],
                                 [-0.0162, 0.1323, -0.0027, 0.9337, 0.1015],
                                 [0.0537, -0.1268, -0.0002, 0.1015, 0.8847]],
                                [[0.7580, -0.0814, 0.0095, -0.3080, -0.0237],
                                 [-0.0814, 0.6195, 0.0068, -0.0540, -0.2622],
                                 [0.0095, 0.0068, 0.9854, 0.0069, 0.0055],
                                 [-0.3080, -0.0540, 0.0069, 0.5697, 0.0051],
                                 [-0.0237, -0.2622, 0.0055, 0.0051, 0.7933]]]
    }]
    return (outcar_file, expected_site_occupation_matrices)


@pytest.fixture
def orbital_occupation_test_cases(orbital_occupation_case_1,
                                  orbital_occupation_case_2):
    return [
        orbital_occupation_case_1,
        orbital_occupation_case_2,
    ]

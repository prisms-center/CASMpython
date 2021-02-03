import os.path
import pytest
import numpy as np

import casm.vasp.io


def test_OrbitOccupation_list_init():
    """ Test constructing OrbitOccupation """
    for input_matrix_type in ['list', 'array']:
        for l_quantum_number in range(4):
            test_matrix_a = np.identity(2 * l_quantum_number + 1)
            test_matrix_b = -np.identity(2 * l_quantum_number + 1)
            if input_matrix_type == 'list':
                test_matrix_a = test_matrix_a.tolist()
                test_matrix_b = test_matrix_b.tolist()
            for spin_polarized in [True, False]:
                if spin_polarized:
                    test_occupation = casm.vasp.io.OrbitalOccupation(
                        test_matrix_a, test_matrix_b)
                else:
                    test_occupation = casm.vasp.io.OrbitalOccupation(
                        test_matrix_a)
            assert test_occupation.l_quantum_number == l_quantum_number
            assert test_occupation.spin_polarized == spin_polarized
            assert np.array_equal(test_occupation.matrices[0], test_matrix_a)
            if spin_polarized:
                assert len(test_occupation.matrices) == 2
                assert np.array_equal(test_occupation.matrices[1],
                                      test_matrix_b)
            else:
                assert len(test_occupation.matrices) == 1


def test_read_occupation_matrices(orbital_occupation_test_cases):
    """ Test casm.vasp.io.Outcar reading orbital occupation matrices """

    # orbital_occupation_test_cases:
    #   list of (datadir, expected_site_occupation_matrices)

    for test_case in orbital_occupation_test_cases:
        datadir, expected_site_occupation_matrices = test_case
        outcar_file = os.path.join(datadir, "OUTCAR")
        outcar = casm.vasp.io.Outcar(outcar_file)

        assert outcar.complete
        for site in expected_site_occupation_matrices:
            site_index = site['site_index']
            occupation_matrices = site['occupation_matrices']
            for spin_channel, occupation_matrix in enumerate(
                    occupation_matrices):
                assert np.allclose(
                    outcar.orbital_occupations[site_index].
                    matrices[spin_channel], np.array(occupation_matrix))


def test_write_occupation_matrices(orbital_occupation_test_cases, tmpdir):
    """ Test writing orbital occupation matrices """

    # orbital_occupation_test_cases:
    #   list of (datadir, expected_site_occupation_matrices)

    for test_case in orbital_occupation_test_cases:
        datadir, expected_site_occupation_matrices = test_case

        occupations = {}
        for site in expected_site_occupation_matrices:
            occupations[site['site_index']] = casm.vasp.io.OrbitalOccupation(
                *tuple(site['occupation_matrices']))

        output_file = tmpdir / 'OCCMATRIX'
        casm.vasp.io.write_occupations(output_file, occupations)

        with open(output_file, 'r') as output:
            expected_occmatrix_file = os.path.join(datadir, 'OCCMATRIX')
            with open(expected_occmatrix_file, 'r') as expected_output:
                assert output.read() == expected_output.read()

import pytest
import numpy as np

import casm.misc.matrix


def test_canonical_unroll_index_list():
    expected_indices = {
        1: [(0, 0)],
        2: [(0, 0), (1, 1), (0, 1)],
        3: [(0, 0), (1, 1), (2, 2), (1, 2), (0, 2), (0, 1)],
        4: [(0, 0), (1, 1), (2, 2), (3, 3), (2, 3), (1, 3), (0, 3), (0, 2),
            (0, 1), (1, 2)],
        5: [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (3, 4), (2, 4), (1, 4),
            (0, 4), (0, 3), (0, 2), (0, 1), (1, 2), (2, 3), (1, 3)]
    }

    for dim in expected_indices.keys():
        assert casm.misc.matrix.canonical_unroll_index_list(
            dim) == expected_indices[dim]


def test_reduction_matrix():
    expected_matrices = {}
    expected_matrices[5] = [
        [
            1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
            0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 1
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            1 / np.sqrt(2), 0, 0, 0, 1 / np.sqrt(2), 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0,
            0, 0, 0, 0, 1 / np.sqrt(2), 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 1 / np.sqrt(2), 0, 0, 0
        ],
        [
            0, 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 1 / np.sqrt(2), 0, 0, 0, 0
        ],
        [
            0, 0, 0, 1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 0, 1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 1 / np.sqrt(2), 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0, 1 / np.sqrt(2), 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0,
            1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0,
            1 / np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0
        ]
    ]

    for dim in expected_matrices.keys():
        assert casm.misc.matrix.reduction_matrix(
            dim).tolist() == expected_matrices[dim]


def test_unroll_reroll_symmetric_matrix():
    test_vectors = []
    test_matrices = []
    test_vectors.append(range(6))
    test_matrices.append([[0, 5 / np.sqrt(2), 4 / np.sqrt(2)],
                          [5 / np.sqrt(2), 1, 3 / np.sqrt(2)],
                          [4 / np.sqrt(2), 3 / np.sqrt(2), 2]])
    test_vectors.append(range(15))
    test_matrices.append([
        [0, 11 / np.sqrt(2), 10 / np.sqrt(2), 9 / np.sqrt(2), 8 / np.sqrt(2)],
        [11 / np.sqrt(2), 1, 12 / np.sqrt(2), 14 / np.sqrt(2), 7 / np.sqrt(2)],
        [10 / np.sqrt(2), 12 / np.sqrt(2), 2, 13 / np.sqrt(2), 6 / np.sqrt(2)],
        [9 / np.sqrt(2), 14 / np.sqrt(2), 13 / np.sqrt(2), 3, 5 / np.sqrt(2)],
        [8 / np.sqrt(2), 7 / np.sqrt(2), 6 / np.sqrt(2), 5 / np.sqrt(2), 4]
    ])

    for i, vec in enumerate(test_vectors):
        mat = test_matrices[i]
        assert np.allclose(casm.misc.matrix.unroll_symmetric_matrix(mat),
                           np.array(vec))
        assert np.allclose(casm.misc.matrix.reroll_symmetric_matrix(vec),
                           np.array(mat))


def test_is_zero():
    assert casm.misc.matrix.is_zero(np.zeros((5, 5)))
    assert casm.misc.matrix.is_zero(1e-09 * np.ones((3, 3)), tol=1e-08)
    assert not casm.misc.matrix.is_zero(1e-07 * np.ones((3, 3)), tol=1e-08)
    assert not casm.misc.matrix.is_zero(np.ones((1, 15)))

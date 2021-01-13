import numpy as np


def canonical_unroll_index_list_recursive(n, origin, current_list):
    """Recursive helper function for canonical_unroll_index_list"""
    o_i, o_j = origin
    for k_sw in range(n):
        current_list.append((o_i + k_sw, o_j + k_sw))
    for k_n in range(n - 1):
        current_list.append((o_i + n - 2 - k_n, o_j + n - 1))
    for k_w in range(n - 2):
        current_list.append((o_i, o_j + n - 2 - k_w))
    if n >= 3:
        return canonical_unroll_index_list_recursive(n - 3, (o_i + 1, o_j + 2),
                                                     current_list)
    else:
        return current_list


def canonical_unroll_index_list(n):
    """Returns an ordered list of indices defining the canonical unrolling of an n by n matrix"""
    return canonical_unroll_index_list_recursive(n, (0, 0), [])


def vectorized_index(i, j, n):
    """Returns the index corresponding to entry i,j in a column-wise vectorization of an n by n matrix"""
    return n * i + j


def reduction_matrix(n):
    """Returns the m by n^2 reduction_matrix matrix that transforms the dimension n^2
        vectorization V of a symmetric n by n matrix U into a vector T of
        dimension m corresponding to the independent elements of U,
        unrolled canonically, with the off-diagonal elements being multiplied by sqrt(2)
    """
    off_diagonal = 1 / np.sqrt(2)
    index_list = canonical_unroll_index_list(n)
    m = len(index_list)
    reduction_matrix = np.zeros((m, n**2))
    for k, (i, j) in enumerate(index_list):
        if i == j:
            reduction_matrix[k, vectorized_index(i, j, n)] = 1
        else:
            reduction_matrix[k, vectorized_index(i, j, n)] = off_diagonal
            reduction_matrix[k, vectorized_index(j, i, n)] = off_diagonal
    return reduction_matrix


def unroll_symmetric_matrix(matrix):
    """Returns the vector that is the unrolled version of the symmetrix matrix given"""
    matrix = np.array(matrix)
    m, n = matrix.shape
    assert (m == n)
    vectorized = matrix.flatten(order='F')
    reduction = reduction_matrix(n)
    return np.matmul(reduction, vectorized)


def reroll_symmetric_matrix(unrolled):
    """Returns the re-rolled symmetric matrix corresponding to the given vector"""
    unrolled = np.array(unrolled)
    n = int(np.sqrt(2 * len(unrolled) + 0.25) -
            0.5)  # inverse of triangular number
    reduction = reduction_matrix(n)
    vectorized = np.matmul(reduction.transpose(), unrolled)
    return np.reshape(vectorized, (n, n), order='F')


def is_zero(array, tol=1e-08):
    """Returns True if the given array is equal to zero, within the given tolerance"""
    return np.allclose(array, np.zeros(array.shape), atol=tol)

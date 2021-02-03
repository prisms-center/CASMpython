import numpy as np
from casm.misc import matrix


class OrbitalOccupationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class OrbitalOccupation(object):
    """Orbital occupation information for a single site. Contains:
        spin_polarized : bool, whether the orbital occupation is spin-polarized
        l_quantum_number : int, the l quantum number of the specified orbitals
        matrices : list, one or two numpy arrays corresponding to the occupation matrices of each spin channel
    """
    def __init__(self, occupation_matrix_a, occupation_matrix_b=None):
        """Initialize occupation from one or two matrices,
            which can be given as lists of lists or numpy arrays
        """
        self.spin_polarized = False
        occupation_matrix_a = np.array(occupation_matrix_a)
        ma, na = occupation_matrix_a.shape
        if (ma == na and na % 2 == 1):
            self.l_quantum_number = int((na - 1) / 2)
            self.matrices = [occupation_matrix_a]
        else:
            raise OrbitalOccupationError(
                'Occupation matrix a is the wrong shape')
        if occupation_matrix_b is not None:
            occupation_matrix_b = np.array(occupation_matrix_b)
            self.spin_polarized = True
            mb, nb = occupation_matrix_b.shape
            if (mb == nb and nb == na):
                self.matrices.append(occupation_matrix_b)
            else:
                raise OrbitalOccupationError(
                    'Occupation matrices a and b have different shapes')

    def get_occext_string(self, site_number):
        """Output a string containing the orbital occupation information using the OCCMATRIX format specified by
            https://github.com/WatsonGroupTCD/Occupation-matrix-control-in-VASP/blob/master/README.md
            site_number : int, POSCAR site number to be written
        """
        def matrix_to_string(matrix):
            return '\n'.join('\t'.join(f'{entry:.4f}' for entry in row)
                             for row in matrix)

        output_string = f'{site_number}\t{self.l_quantum_number}\t{int(self.spin_polarized)+1}\n'
        output_string += 'spin channel 1\n'
        output_string += matrix_to_string(self.matrices[0]) + '\n'
        if self.spin_polarized:
            output_string += 'spin channel 2\n'
            output_string += matrix_to_string(self.matrices[1]) + '\n'
        output_string += '\n'
        return output_string

    def to_vector(self):
        """Return a vector of the unrolled occupation matrix/matrices that can be read as a CASM attribute.
            In the spin-polarized case, the vectors corresponding to the up/down occupation matrices are concatenated.
        """
        vector = []
        for occupation_matrix in self.matrices:
            vector += matrix.unroll_symmetric_matrix(occupation_matrix)
        return vector


def write_occupations(filename, occupations):
    """Write a dict of occupations out to an OCCMATRIX-like file
        filename : str, output filename
        occupations : dict of OrbitalOccupation, site occupations stored using site indices (from 0) as keys
    """
    with open(filename, 'w') as output_file:
        output_file.write(str(len(occupations.keys())) + '\n')
        for site_number in occupations.keys():
            output_file.write(occupations[site_number].get_occext_string(
                site_number + 1))  # VASP indexes sites from 1

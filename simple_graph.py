# a simple graph is an undirected graph with no self-loops. we represent it
# with only the upper triangle in column-major order

import base64
import itertools
import numpy as np

def base64_to_matrix(b64):
    return triangle_to_matrix(base64_to_triangle(b64))

def triangle_to_base64(triangle):
    triangle_bytes = np.packbits(triangle, bitorder='little')
    return base64.b64encode(triangle_bytes).decode('ascii')

def base64_to_triangle(b64):
    triangle_bytes = np.frombuffer(base64.b64decode(b64), dtype=np.uint8)
    byte_index = np.nonzero(triangle_bytes)[0][-1]
    last_byte = triangle_bytes[byte_index]
    bit_count = 8 * byte_index + int(last_byte).bit_length()
    # https://oeis.org/A002024
    n = (np.math.isqrt(8 * bit_count) + 1) // 2
    # https://oeis.org/A000217
    triangle_length = n * (n + 1) // 2
    triangle = np.unpackbits(
        triangle_bytes,
        bitorder='little',
        count=triangle_length,
    )
    return triangle.astype(bool)

def base64_to_nodes(b64):
    triangle_bytes = np.frombuffer(base64.b64decode(b64), dtype=np.uint8)
    byte_index = np.nonzero(triangle_bytes)[0][-1]
    last_byte = triangle_bytes[byte_index]
    bit_count = 8 * byte_index + int(last_byte).bit_length()
    # https://oeis.org/A002024
    n = (np.math.isqrt(8 * bit_count) + 1) // 2
    return n + 1

def matrix_to_triangle(matrix):
    square_to_triangle = triu_indices_flat(len(matrix))
    return matrix.flatten()[square_to_triangle]

def triangle_to_matrix(triangle):
    nodes = triangle_length_to_nodes(len(triangle))
    triangle_to_square = square_indices_flat(nodes)
    matrix = triangle[triangle_to_square]
    matrix[::nodes + 1] = 0
    return matrix.reshape((nodes, nodes))

def permute_triangle(triangle, permutation):
    nodes = triangle_length_to_nodes(len(triangle))
    triangle_to_square = square_indices_flat(nodes)
    square = triangle[triangle_to_square].reshape((nodes, nodes))
    # add : in both orientations in case permutation is tuple
    square = permute_matrix(square, permutation)
    return matrix_to_triangle(square)

def permute_matrix(matrix, permutation):
    return matrix[:, permutation][permutation, :]

def get_canonical_permutation(triangle):
    nodes = triangle_length_to_nodes(len(triangle))
    transformer = get_triangle_permutations(nodes)
    triangles = triangle[transformer]
    order = np.lexsort(triangles.T)
    return triangles[order[0]]

def triangle_length_to_nodes(length):
    # https://en.wikipedia.org/wiki/Triangular_number#Triangular_roots_and_tests_for_triangular_numbers
    # the final + is not a typo, it adds 1 to the final result on purpose
    return (np.math.isqrt(8 * length + 1) + 1) // 2

transformers = {}
def get_triangle_permutations(n):
    try:
        return transformers[n]
    except KeyError:
        pass

    squares = get_square_permutations(n)
    flat_squares = squares.reshape((len(squares), n * n))
    square_to_triangle = triu_indices_flat(n)
    square_to_triangles = flat_squares[:, square_to_triangle]
    triangle_to_square = square_indices_flat(n)
    triangle_to_triangles = triangle_to_square[square_to_triangles]
    transformers[n] = triangle_to_triangles
    return triangle_to_triangles

def square_indices_flat(n):
    # inverse of triu_indices_flat for a symmetric matrix
    row = np.arange(n)
    column = row[:, np.newaxis]
    out = np.maximum(row, column)
    out *= (out - 1)
    out //= 2
    out += np.minimum(row, column)
    out = out.flatten()
    # diagonal is undefined, but keep it in range for convenience
    out[-1] = 0
    return out

def triu_indices_flat(n):
    # for a square array with values 0 ... n*n-1, get a 1D array consisting of
    # all items in the upper triangle, in column-major order
    return np.concatenate([np.arange(i, i * (n + 1), n) for i in range(n)])

def get_square_permutations(n):
    # get all permutations of a square array with values 0 ... n*n-1 such that
    # rows and columns are permuted in the same order
    permutations = np.fromiter(
        itertools.permutations(range(n)),
        dtype=np.dtype((int, n)),
        count=np.math.factorial(n),
    )
    rows = permutations[..., np.newaxis, :]
    columns = permutations[..., np.newaxis]
    result = rows + n * columns
    return result

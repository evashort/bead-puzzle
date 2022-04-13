import itertools
import math
import numpy as np

def get_hole_slice(n, i):
    # if you have an array containing (in lexicographic order) all possible
    # permutations of n distinct items, and the array has n dimensions and
    # shape (n, n-1, ..., 1), this function returns a slice that, when applied
    # to the array, selects the permutations where the hole is at index i of
    # the permutation. "hole" means the item of the permutation that comes
    # first in sort order.
    return i * np.index_exp[1:] + np.index_exp[0] \
        + (n - i - 1) * np.index_exp[:]

x = np.array(
    [
        int(''.join(permutation))
        for permutation in itertools.permutations('012345')
    ]
)
x_view = x.reshape(range(6, 0, -1))
print(x_view[get_hole_slice(6, 1)].flatten())

def missing_diagonal(length):
    # missing_diagonal(4) = [[1, 2, 3],
    #                        [0, 2, 3],
    #                        [0, 1, 3],
    #                        [0, 1, 2]]
    result = (np.arange(length) + np.arange(1, length)[:, np.newaxis]).reshape(length, -1)
    result %= length
    return result

def tuplet_grow(arr, new_length):
    # tuplet_grow([0, 1, 2], 4) = [[0, 0, 0],
    #                              [0, 1, 1],
    #                              [1, 1, 2],
    #                              [2, 2, 2]]
    while len(arr) < new_length:
        arr = np.broadcast_to(
            arr[:, np.newaxis],
            (len(arr), len(arr) + 1) + arr.shape[1:],
        ).reshape(
            (len(arr) + 1,) + arr.shape,
        )

    return arr

def pad_dims_right(arr, new_ndim):
    return arr.reshape(arr.shape + (1,) * (new_ndim - arr.ndim))

def get_moved_slice(n, i, j):
    # if you have an array containing (in lexicographic order) all possible
    # permutations of n distinct items, and the array has n dimensions and
    # shape (n, n-1, ..., 1), and 0 <= i < j < n, this function returns a
    # slice that, when applied to the array, selects the permutations that
    # would be the result of swapping the items at indices i and j for each
    # permutation where the hole is at index j. the resulting permutations
    # will be ordered by their corresponding pre-swap permutation. "hole"
    # means the item of the permutation that comes first in sort order. I have
    # no explanation for how this function works; I wrote it by making a
    # spreadsheet of desired results and looking for patterns.
    return np.index_exp[1:] * i + np.index_exp[0] \
        + sum(
            (
                (
                    pad_dims_right(
                        tuplet_grow(missing_diagonal(n - k), n - i - 1),
                        j - i,
                    ),
                )
                for k in range(i + 1, j)
            ),
            start=(),
        ) + (
            tuplet_grow(np.arange(n - j), n - i - 1),
        )

def get_move_slices(n, i, j):
    swap = j < i
    if swap:
        i, j = j, i

    hole_slice = get_hole_slice(n, j)
    moved_slice = get_moved_slice(n, i, j)
    return (moved_slice, hole_slice) if swap else (hole_slice, moved_slice)

graph = np.array(
    [
        [0,1,1,0,0,1],
        [1,0,1,0,0,0],
        [1,1,0,1,0,0],
        [0,0,1,0,1,0],
        [0,0,0,1,0,1],
        [1,0,0,0,1,0],
    ],
    dtype=bool,
)
graph = np.array(
    [
        [0,1,1,1],
        [1,0,1,0],
        [1,1,0,1],
        [1,0,1,0],
    ],
    dtype=bool,
)
# rotation is the number of indices by which to shift all values to the right
distinct_rotations = np.tile(graph, (2, 2))[1:, 1:]
_, distinct_rotations = np.unique(
    np.lib.stride_tricks.as_strided(
        distinct_rotations,
        (min(graph.shape),) + graph.shape,
        (sum(distinct_rotations.strides),) + distinct_rotations.strides,
    )[::-1],
    axis=0,
    return_index=True,
)
distances = np.full(
    2 * (math.factorial(len(graph)),),
    float('inf'),
    np.float16,
)
range_view = np.arange(len(distances)).reshape(range(len(graph), 0, -1))
for i, j in zip(*np.nonzero(graph)):
    i_slice, j_slice = get_move_slices(len(graph), i, j)
    distances[
        range_view[j_slice].flatten(),
        range_view[i_slice].flatten(),
    ] = 1

np.fill_diagonal(distances, 0)

def get_swap_slices(n, i):
    if 0 <= i < n - 1:
        src_stop = i - 1 if i > 0 else None
        yield np.index_exp[i + 1 : src_stop : -1], np.index_exp[i : i + 2]

    if i > 0:
        low_slice = np.index_exp[: i]
        for src_slice, dst_slice in get_swap_slices(n - 1, i - 1):
            yield low_slice + src_slice, low_slice + dst_slice

    if i < n - 2:
        high_slice = np.index_exp[i + 2 :]
        for src_slice, dst_slice in get_swap_slices(n - 1, i):
            yield high_slice + src_slice, high_slice + dst_slice

y = np.zeros(720, dtype=int)
y_view = y.reshape(range(6, 0, -1))
for src_slice, dst_slice in get_swap_slices(6, 4):
    y_view[dst_slice] = x_view[src_slice]

print(y)

def get_distance_product(a, b, out=None, temp=None):
    # https://en.wikipedia.org/wiki/Min-plus_matrix_multiplication
    a = np.asanyarray(a)
    b = np.asanyarray(b)
    if out is None:
        out = np.empty(
            np.broadcast_shapes(
                a.shape[:-1] + (1,),
                b.shape[:-2] + (1, b.shape[-1])),
            np.result_type(a, b),
        )

    if temp is None:
        temp = np.empty(
            np.broadcast_shapes(a.shape[:-2] + (1, 1), b.shape),
            np.result_type(a, b),
        )

    for i, row in enumerate(np.moveaxis(a, -2, 0)):
        np.add(row[..., np.newaxis], b, out=temp)
        np.min(temp, axis=-2, out=out[..., i, :])

    return out

print(
    get_distance_product(
        [[[1, 0, 2], [0, 2, 3]], [[1, 0, 2], [0, 2, 3]]],
        [[2, 1, 1, 0], [0, 1, 2, 1], [2, 0, 0, 2]],
    )
)
# 1 0 2   2 1 1 0   0 1 2 1
# 0 2 3 * 0 1 2 1 = 2 1 1 0
#         2 0 0 2

def index_to_permutation(n, i):
    remaining = list(range(n))
    nFactorial = np.product(np.arange(1, n + 1))
    for n in range(n, 0, -1):
        nFactorial //= n
        index, i = divmod(i, nFactorial)
        yield remaining[index]
        del remaining[index]

print(''.join(map(str, index_to_permutation(6, 349)))) # 253041

out = np.ones_like(distances)
temp = np.empty_like(distances)
while out.any():
    get_distance_product(distances, distances, out, temp)
    distances, out = out, distances
    np.not_equal(distances, out, out=out)

def get_rotation_slice(n):
    # for n = 4, returns a slice that selects 0123, 1230, 2301, 3012 out of a
    # lexicographically ordered list of all permutations of 0, 1, 2, and 3
    result = np.ones(n, dtype=int)
    for i in range(n - 1, 0, -1):
        result *= i
        result[:i] += 1

    result *= np.arange(n)
    return result

rotation_slice = get_rotation_slice(len(graph))[distinct_rotations]
# we can require the final permutation to be a rotation of 0123...n without
# losing generality
distances = distances[:, rotation_slice]
np.nan_to_num(distances, copy=False, posinf=-1)
max_distance = distances.max()
print(max_distance)

np.equal(distances, max_distance, out=distances)
for start_index, rotation_index in zip(*np.nonzero(distances)):
    rotation = distinct_rotations[rotation_index]
    start = tuple(index_to_permutation(len(graph), start_index))
    # shift everything right. greater rotation means greater right shift.
    # note that successive final permutations e.g. 0123, 1230, 2301... are
    # increasingly left shifted. the rightward shift cancels that out and puts
    # the final permutation in standard position 0123
    start = start[len(start) - rotation :] + start[: len(start) - rotation]
    print(
        rotation,
        ''.join(map(str, start)),
        '->',
        ''.join(map(str, range(len(graph)))),
    )

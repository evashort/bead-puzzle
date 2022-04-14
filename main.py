import itertools
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
    moved_slice = get_moved_slice(n, i, j) if i != j else hole_slice
    return (moved_slice, hole_slice) if swap else (hole_slice, moved_slice)

def to_bytes(arr):
    if arr.dtype != np.bool8:
        raise TypeError(f'dtype must be bool8, not {arr.dtype}')

    return np.packbits(arr.view(np.uint8)).tobytes()

print(
    to_bytes(np.array([[0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 1, 0]], dtype=bool)),
) # 20,32 = b'\x14 '

def all_binary_arrays(length):
    arr = np.ones((2 ** length, length), dtype=bool)
    power = 1
    for place in range(length):
        arr.reshape(-1, 2, power, length)[:, 0, :, place] = 0
        power *= 2

    return arr

print(all_binary_arrays(4))

def is_graph_contiguous(graph):
    graph = np.asanyarray(graph)
    if np.any(np.count_nonzero(graph, axis=1) <= 1):
        return False

    seen = set()
    stack = [0]
    while stack:
        index = stack.pop()
        if index not in seen:
            stack.extend(np.nonzero(graph[index])[0])
            seen.add(index)

    return len(seen) == len(graph)

print(is_graph_contiguous([
    [0,1,1],
    [1,0,1],
    [1,1,0],
])) # true
print(is_graph_contiguous([
    [0,1,0],
    [1,0,1],
    [0,1,0],
])) # false
print(is_graph_contiguous([
    [0,1,1,0,0,0],
    [1,0,1,0,0,0],
    [1,1,0,0,0,0],
    [0,0,0,0,1,1],
    [0,0,0,1,0,1],
    [0,0,0,1,1,0],
])) # false

def get_rotations(arr):
    # returns an array where the element at index i is arr shifted in the
    # positive direction by i indices on all axes, e.g. [0,1,2,3] -> [3,0,1,2]
    arr = np.asanyarray(arr)
    return np.moveaxis(
        np.diagonal(
            np.lib.stride_tricks.sliding_window_view(
                np.tile(arr, (2,) * arr.ndim)[(np.s_[1:],) * arr.ndim],
                arr.shape,
            )[(np.s_[::-1],) * arr.ndim],
        ),
        -1,
        0,
    )

print(get_rotations([[0, 1, 2], [3, 4, 5]])) # 012/345 534/201

def get_distinct_rotations(arr):
    _, indices = np.unique(get_rotations(arr), return_index=True, axis=0)
    return indices

def get_edge_lengths(nodes):
    # get_edge_lengths(6) = [[0, 1, 2, 3, 2, 1],
    #                        [1, 0, 1, 2, 3, 2],
    #                        [2, 1, 0, 1, 2, 3],
    #                        [3, 2, 1, 0, 1, 2],
    #                        [2, 3, 2, 1, 0, 1],
    #                        [1, 2, 3, 2, 1, 0]]
    return np.lib.stride_tricks.sliding_window_view(
        np.tile(
            np.minimum(np.arange(nodes), np.arange(nodes, 0, -1)),
            2,
        )[1:],
        nodes,
    )[::-1]

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

def get_good_graphs(nodes):
    base_graph = np.zeros((nodes, nodes), dtype=bool)
    triu_indices = np.triu_indices(nodes, k=1)
    seen = set()
    edge_lengths = get_edge_lengths(nodes)
    for triu_values in all_binary_arrays(len(triu_indices[0])):
        base_graph[triu_indices] = triu_values
        base_graph.T[triu_indices] = triu_values
        if to_bytes(base_graph) in seen \
            or not is_graph_contiguous(base_graph):
            continue

        best_total_edge_length = float('inf')
        graph = base_graph
        for permutation in map(list, itertools.permutations(range(nodes))):
            permuted_graph = base_graph[permutation][:, permutation]
            seen.add(to_bytes(permuted_graph))
            total_edge_length = np.tensordot(permuted_graph, edge_lengths)
            if total_edge_length < best_total_edge_length:
                best_total_edge_length = total_edge_length
                graph = permuted_graph

        yield graph

def get_initial_distances(graph, out=None):
    graph = np.asanyarray(graph)
    if out is None:
        out = np.empty(
            2 * (np.product(np.arange(1, len(graph) + 1)),),
            dtype=np.float16,
        )

    out.fill(float('inf'))
    range_view = np.arange(len(out)).reshape(range(len(graph), 0, -1))
    for i, j in zip(*np.nonzero(graph)):
        i_slice, j_slice = get_move_slices(len(graph), i, j)
        out[
            range_view[j_slice].flatten(),
            range_view[i_slice].flatten(),
        ] = 1

    np.fill_diagonal(out, 0)
    return out

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

def get_rotation_slice(n):
    # for n = 4, returns a slice that selects 0123, 1230, 2301, 3012 out of a
    # lexicographically ordered list of all permutations of 0, 1, 2, and 3
    result = np.ones(n, dtype=int)
    for i in range(n - 1, 0, -1):
        result *= i
        result[:i] += 1

    result *= np.arange(n)
    return result

def get_max_distance_and_puzzles(n, distances, distinct_rotations):
    rotation_slice = get_rotation_slice(n)[distinct_rotations]
    # we can require the final permutation to be a rotation of 0123...n
    # without losing generality
    distances = distances[:, rotation_slice]
    np.nan_to_num(distances, copy=False, posinf=-1)
    max_distance = int(distances.max())
    np.equal(distances, max_distance, out=distances)
    puzzles = []
    for start_index, rotation_index in zip(*np.nonzero(distances)):
        start = tuple(index_to_permutation(n, start_index))
        rotation = distinct_rotations[rotation_index]
        # shift everything right. greater rotation means greater right shift.
        # note that successive final permutations e.g. 0123, 1230, 2301... are
        # increasingly left shifted. the rightward shift cancels that out and
        # puts the final permutation in standard position 0123
        start = start[n - rotation :] + start[: n - rotation]
        puzzles.append((start, rotation))

    return max_distance, puzzles

def get_graphs_and_puzzles(nodes):
    distances = None
    out = None
    temp = None
    for graph in get_good_graphs(nodes):
        distances = get_initial_distances(graph, out=distances)
        if out is None:
            out = np.empty_like(distances)

        if temp is None:
            temp = np.empty_like(distances)

        out.reshape(-1)[0] = 1
        while out.any():
            get_distance_product(distances, distances, out, temp)
            distances, out = out, distances
            np.not_equal(distances, out, out=out)

        max_distance, puzzles = get_max_distance_and_puzzles(
            nodes,
            distances,
            get_distinct_rotations(graph),
        )

        yield graph, max_distance, puzzles

if __name__ == '__main__':
    for graph, max_distance, puzzles in get_graphs_and_puzzles(4):
        print(graph)
        print(max_distance)
        for start, rotation in puzzles:
            print(rotation, ''.join(map(str, start)), '-> 0123')

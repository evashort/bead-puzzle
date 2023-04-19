import collections
import itertools
import json
import numpy as np
from pathlib import Path
import permute
import random
import simple_graph

iterations = 1000
src_folder = Path('graphs')
dst_folder = Path('difficulty')
dst_folder.mkdir(exist_ok=True)
final_path = Path('src/assets/graphs.json')
graphs = []
for i, src_path in enumerate(src_folder.iterdir()):
    print(f'{i + 1} {src_path.stem}', flush=True)
    with open(src_path, encoding='utf-8') as f:
        graph = json.load(f)

    dst_path = dst_folder / src_path.name
    difficulty = None
    try:
        f = open(dst_path, encoding='utf-8')
    except FileNotFoundError:
        pass
    else:
        with f:
            try:
                difficulty = json.load(f)
            except json.decoder.JSONDecodeError:
                pass

    node_count = simple_graph.base64_to_nodes(graph['id'])
    matrix = simple_graph.base64_to_matrix(graph['layout'])
    if difficulty is None:
        goal = tuple(range(1, node_count))
        total_difficulty = 0
        for i in range(iterations):
            puzzle = random.choice(graph['puzzles'])
            start = permute.from_index(puzzle['start'], node_count)
            beads = tuple(start.index(i) for i in range(1, node_count))
            hole, = set(goal + (0,)).difference(beads)
            edges = {}
            rotation = puzzle['rotation']
            for a, b in zip(*np.nonzero(matrix)):
                if a < b:
                    a, b = ((x + rotation) % node_count for x in (a, b))
                    edges.setdefault(a, set()).add(b)
                    edges.setdefault(b, set()).add(a)

            seen = collections.Counter()
            moves = 0
            while beads != goal:
                seen[beads] += 1
                choices = {
                    b: tuple(hole if bead == b else bead for bead in beads)
                    for b in edges[hole]
                }
                moves += 1
                scores = {
                    b: (
                        seen[choice],
                        sum(
                            node != bead
                            for bead, node in enumerate(choice, start=1)
                        ),
                    ) for b, choice in choices.items()
                }
                min_score = min(scores.values())
                hole, beads = random.choice(
                    [
                        (b, choices[b]) for b, score in scores.items()
                        if score <= min_score
                    ],
                )

            total_difficulty += moves

        difficulty = total_difficulty / iterations
        with open(dst_path, mode='w', encoding='utf-8', newline='\n') as f:
            json.dump(difficulty, f)

        # reduce precision before sorting
        with open(dst_path, encoding='utf-8') as f:
            difficulty = json.load(f)

    graph['difficulty'] = difficulty

    edges = {}
    for a, b in zip(*np.nonzero(matrix)):
        if a < b:
            edges.setdefault(a, set()).add(b)
            edges.setdefault(b, set()).add(a)

    # depth-first search all states reachable from goal
    stack = [tuple(range(node_count))]
    seen = set()
    while stack:
        state = stack.pop()
        if state in seen:
            continue

        seen.add(state)
        for node in edges[state.index(0)]:
            chosen = state[node]
            stack.append(
                tuple(
                    chosen if bead == 0
                    else 0 if bead == chosen
                    else bead
                    for bead in state
                )
            )

    graph['states'] = len(seen)

    graphs.append(graph)

graphs.sort(key=lambda graph: graph['difficulty'])

size_graphs = {}
for graph in graphs:
    node_count = simple_graph.base64_to_nodes(graph['id'])
    size_graphs.setdefault(node_count, []).append(graph)

size_matrices = {}
size_permutations = {}
for size, graph_list in size_graphs.items():
    matrices = np.zeros((len(graph_list), size, size), dtype=bool)
    for i, graph in enumerate(graph_list):
        matrices[i] = simple_graph.base64_to_matrix(graph['layout'])

    matrices = matrices.reshape(len(graph_list), -1)
    size_matrices[size] = matrices
    permutations = np.array(
        list(itertools.permutations(range(size)))
    )
    permutations = (
        permutations[:, np.newaxis] + permutations[:, :, np.newaxis] * size
    ).reshape(-1, size * size)
    size_permutations[size] = permutations

# find easier subgraphs with higher distance and more states because they
# are better
# x is a subgraph of y <=> not any(x & ~y) <=> x dot ~y == 0
for size, matrices in size_matrices.items():
    permutations = size_permutations[size]
    graph_list = size_graphs[size]
    for i, matrix in enumerate(matrices):
        superior = np.logical_not(
            np.all(
                np.matmul(
                    matrices[:i],
                    np.logical_not(matrix)[permutations].T,
                ),
                axis=1,
            ),
        )
        graph = graph_list[i]
        distance = graph['distance']
        states = graph['states']
        graph['superior'] = [
            graph_list[j]['id'] for j in np.nonzero(superior)[0]
            if graph_list[j]['distance'] >= distance \
                and graph_list[j]['states'] >= states
        ]

    # flag graphs with a loop containing all nodes and an edge between two
    # consecutive nodes because they can be solved with a boring algorithm
    loop_matrix = np.zeros(size * size, dtype=bool)
    loop_matrix[1::size + 1] = True
    loop_matrix[size::size + 1] = True
    loop_matrix[size - 1] = True
    loop_matrix[size * (size - 1)] = True
    loop_matrix[2] = True
    loop_matrix[2 * size] = True
    has_loop = np.logical_not(
        np.all(
            np.matmul(
                np.logical_not(matrices),
                loop_matrix[permutations].T,
            ),
            axis=1,
        ),
    )
    for graph, loop in zip(graph_list, has_loop):
        graph['loop'] = bool(loop)

names_path = 'graph_names.json'
id_names = None
try:
    f = open(names_path, encoding='utf-8')
except FileNotFoundError:
    id_names = {}
else:
    with f:
        id_names = json.load(f)

# sort by difficulty and add new graphs
for graph in graphs:
    id_names[graph['id']] = id_names.pop(graph['id'], '')

with open(names_path, mode='w', encoding='utf-8', newline='\n') as f:
    json.dump(id_names, f, indent=2)

for graph in graphs:
    nodes = simple_graph.base64_to_nodes(graph['id'])
    puzzles = [[] for _ in range(nodes)]
    for puzzle in graph['puzzles']:
        puzzles[puzzle['rotation']].append(puzzle['start'])

    for rotation_puzzles in puzzles:
        rotation_puzzles.sort()

    graph['puzzles'] = puzzles

    id_matrix = simple_graph.base64_to_matrix(graph['id'])
    matrix = simple_graph.base64_to_matrix(graph['layout'])

    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    name = id_names[graph['id']]
    if isinstance(name, dict):
        permutation = np.fromiter(
            map(letters.index, name['layout']),
            dtype=int,
            count=len(name['layout']),
        )
        name = name['name']
        matrix = simple_graph.permute_matrix(matrix, permutation)
        # if nodes = 3,
        # puzzles[0] is all the puzzles where the hole is at index 0 in the original matrix
        # puzzles[1] is all the puzzles where the hole is at index 3 in the original matrix, rotated right by 1 so the hole is at index 0
        # puzzles[2] is all the puzzles where the hole is at index 2 in the original matrix, rotated right by 2 so the hole is at index 0
        # puzzles[3] is all the puzzles where the hole is at index 1 in the original matrix, rotated right by 3 so the hole is at index 0
        # before applying the permutation to the puzzles, we have to rotate it
        # to match the puzzles. rotating a permutation right means adding to
        # each element mod N so it selects inputs further to the right, and
        # rotating the elements right so it produces outputs further to the
        # right
        # for puzzles[1], this means adding 1 to each element mod N and shifting the elements right 1 space
        # for puzzles[2], this means adding 2 to each element mod N and shifting the elements right 2 spaces
        # for puzzles[3], this means adding 3 to each element mod N and shifting the elements right 3 spaces
        # however, we need the hole to be in index 0 after applying the
        # premutation, so we shift the elements intil the permutation starts
        # with 0 instead. the number of spaces by which we had to shift the
        # elements right is called new_rotation
        # applying the permutation accounts for the change in the graph
        # layout, but we still have to account for the change in goal. since
        # the old goal was 0,1,2,3, applying the permutation to it gives the
        # permutation itself. in order to get from the permuted old goal to
        # the new goal of 0,1,2,3, we can use the inverse of the permutation
        # as a lookup table for each element in the puzzle, or in other words,
        # use the puzzle as a permutation for the inverse permutation.
        # finally, new_rotation is the negative of the original location of
        # the hole mod N, so it becomes the new index for these puzzles within
        # the puzzles array.
        #
        # here's an example using graph ID Hw== "Sandwich" and layout BACD
        # (swapping the first two nodes). for rotation A, this means moving
        # the hole so the puzzle becomes part of rotation D (not rotation B,
        # think about it):
        #
        # start swap  spin  lookup
        #   0     3     0     0
        #  /|\    |\   /|\   /|\
        # 1 | 3 1-+-0 3-+-2 2-+-1
        #  \|/   \|/    |/    |/
        #   2     2     1     3
        #
        # old goal...       new goal
        #   0     1     0     0
        #  /|\    |\   /|\   /|\
        # 2 | 1 3-+-0 1-+-2 3-+-1
        #  \|/   \|/    |/    |/
        #   2     2     3     2
        #
        # permutation = [1,0,2,3]
        # rotate it so zero comes first: [0,2,3,1]
        # start = [0,3,2,1]
        # apply the rotated pemutation to start: [0,3,2,1][[0,2,3,1]] = [0,2,1,3]
        # invert the rotated permutation: invert([0,2,3,1]) = [0,3,1,2]
        # apply the permuted start to the inverted permutation: [0,3,1,2][[0,2,1,3]] = [0,1,3,2]
        # the result of the last step matches the "lookup" diagram above.
        # "lookup" means taking the beads in the "spin" diagram, finding them
        # in the third "old goal" diagram, and replacing them with the
        # corresponding beads in the "new goal" diagram. that's what the last
        # step effectively does.
        #
        # for rotation B, the hole stays where it was and the result is still in rotation B:
        #
        # start swap  lookup
        #   2     2     1
        #  / \   /|    /|
        # 3---1 3-+-0 3-+-0
        #  \ /   \|/   \|/
        #   0     1     2
        #
        # old goal... new goal
        #   0     0     0
        #  / \   /|    /|
        # 3---1 3-+-2 3-+-1
        #  \ /   \|/   \|/
        #   2     1     2
        #
        # permutation = [1,0,2,3]
        # add 1 to it mod 4: [2,1,3,0]
        # rotate it so zero comes first: [0,2,1,3]
        # start = [2,1,0,3]
        # apply the rotated pemutation to start: [2,1,0,3][[0,2,1,3]] = [2,0,1,3]
        # invert the rotated permutation: invert([0,2,1,3]) = [0,2,1,3]
        # apply the permuted start to the inverted permutation: [0,2,1,3][[2,0,1,3]] = [1,0,2,3]
        # the result of the last step matches the "lookup" diagram above.
        # "lookup" means taking the beads in the "swap" diagram, finding them
        # in the second "old goal" diagram, and replacing them with the
        # corresponding beads in the "new goal" diagram. that's what the last
        # step effectively does.
        new_puzzles = [None] * nodes
        start = np.zeros(nodes, dtype=int)
        for i, rotation_puzzles in enumerate(puzzles):
            new_rotation = -np.where(permutation == -i % nodes)[0][0] % nodes
            rotated = np.roll(permutation, new_rotation)
            rotated += i
            rotated %= nodes
            inverse = permute.invert(rotated)
            for j, puzzle in enumerate(rotation_puzzles):
                permute.from_index(puzzle, start)
                permuted_start = start[rotated]
                new_start = inverse[permuted_start]
                new_puzzle = permute.to_index(new_start)
                rotation_puzzles[j] = new_puzzle

            rotation_puzzles.sort()
            new_puzzles[new_rotation] = rotation_puzzles

        graph['puzzles'] = new_puzzles

    if name is not None and not name.startswith('#'):
        # make sure it starts with A
        empty_rotations = 0
        for i, rotation_puzzles in enumerate(graph['puzzles']):
            if rotation_puzzles:
                empty_rotations = i
                break

        if empty_rotations:
            print(
                f'warning: {name} starts with {letters[empty_rotations]}, '
                f'not A'
            )

    graph['name'] = name
    graph['layout'] = permute.matrix_pair_to_index(id_matrix, matrix)

graphs = [
    graph for graph in graphs
    if graph['name'] is not None and not graph['name'].startswith('#')
]

# put tutorial in order
graphs[0], graphs[1] = graphs[1], graphs[0]

with open(final_path, mode='w', encoding='utf-8', newline='\n') as f:
    json.dump({'graphs': graphs}, f)

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
            while True:
                seen[beads] += 1
                choices = {
                    b: tuple(hole if bead == b else bead for bead in beads)
                    for b in edges[hole]
                }
                moves += 1
                if goal in choices.values():
                    break

                min_seen = min(seen[choice] for choice in choices.values())
                hole, beads = random.choice(
                    [
                        item for item in choices.items()
                        if seen[item[1]] <= min_seen
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

    name = id_names[graph['id']]
    if isinstance(name, dict):
        permutation = [
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(letter)
            for letter in name['layout']
        ]
        name = name['name']
        matrix = simple_graph.permute_matrix(matrix, permutation)
        inverse = permute.invert(permutation)
        # if nodes = 3,
        # puzzles[0] is all the puzzles where the hole is at index 0 in the original matrix
        # puzzles[1] is all the puzzles where the hole is at index 3 in the original matrix, rotated so the hole is at index 0
        # puzzles[2] is all the puzzles where the hole is at index 2 in the original matrix, rotated so the hole is at index 0
        # puzzles[3] is all the puzzles where the hole is at index 1 in the original matrix, rotated so the hole is at index 0
        # before applying the permutation to the puzzles, we have to rotate the hole back to where it was before
        # for puzzles[1], this means shifting the beads left 1 space
        # for puzzles[2], this means shifting the beads left 2 spaces
        # for puzzles[3], this means shifting the beads left 3 spaces
        # after applying the permutation, we have to rotate the hole back to index 0
        # for puzzles[0], this means shifting the beads left by inverse[0] spaces
        # for puzzles[1], this means shifting the beads left by inverse[3] spaces
        # for puzzles[2], this means shifting the beads left by inverse[2] spaces
        # for puzzles[3], this means shifting the beads left by inverse[1] spaces
        # finally, we have to make sure that the index of each puzzle within
        # the puzzles array corresponds the to position of the hole in the
        # permuted matrix the way it used to for the original matrix.
        # new_puzzles[(4 - inverse[0]) % 4] should be the old puzzles[0]
        # new_puzzles[(4 - inverse[3]) % 4] should be the old puzzles[1]
        # new_puzzles[(4 - inverse[2]) % 4] should be the old puzzles[2]
        # new_puzzles[(4 - inverse[1]) % 4] should be the old puzzles[3]
        new_puzzles = [None] * nodes
        for i, rotation_puzzles in enumerate(puzzles):
            for j, puzzle in enumerate(rotation_puzzles):
                rotated = permute.rotate_index(puzzle, -i, nodes)
                permuted = permute.permute_index(rotated, permutation)
                new_puzzle = permute.rotate_index(
                    permuted,
                    -inverse[(nodes - i) % nodes],
                    nodes,
                )
                rotation_puzzles[j] = new_puzzle

            rotation_puzzles.sort()
            new_puzzles[(nodes - inverse[(nodes - i) % nodes]) % nodes] \
                = rotation_puzzles
            
        graph['puzzles'] = new_puzzles

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

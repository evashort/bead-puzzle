import base64
import collections
import itertools
import json
import numpy as np
from pathlib import Path
import random
import sys

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

    if difficulty is None:
        node_count = graph['nodes']
        goal = tuple(range(1, node_count))
        total_difficulty = 0
        for i in range(iterations):
            puzzle = random.choice(graph['puzzles'])
            beads = tuple(puzzle['beads'])
            hole, = set(goal + (0,)).difference(beads)
            edges = {}
            rotation = puzzle['rotation']
            for a, b in graph['edges']:
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

    node_count = graph['nodes']
    edges = {}
    for a, b in graph['edges']:
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

    n = graph['nodes']
    triangle = np.zeros(n * (n - 1) // 2, dtype=bool)
    for a, b in graph['edges']:
        triangle[b * (b - 1) // 2 + a] = True
    graph['id'] = base64.b64encode(np.packbits(triangle)).decode('ascii')
    graphs.append(graph)

graphs.sort(key=lambda graph: graph['difficulty'])

size_graphs = {}
for graph in graphs:
    size_graphs.setdefault(graph['nodes'], []).append(graph)

size_matrices = {}
size_permutations = {}
for size, graph_list in size_graphs.items():
    matrices = np.zeros((len(graph_list), size, size), dtype=bool)
    for i, graph in enumerate(graph_list):
        edges = graph['edges']
        matrices[
            i,
            sum(zip(*edges), start=()),
            sum(list(zip(*edges))[::-1], start=()),
        ] = True

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
    random.seed(graph['id'])
    random.shuffle(graph['puzzles'])
    name = id_names[graph['id']]
    if isinstance(name, dict):
        a_rotation = name['rotation']
        rotation_orders = name.get('puzzles', {})
        name = name['name']

        nodes = graph['nodes']
        for edge in graph['edges']:
            edge[0] = (edge[0] + nodes - a_rotation) % nodes
            edge[1] = (edge[1] + nodes - a_rotation) % nodes

        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        letter_puzzles = {letter: [] for letter in letters[:nodes]}
        for puzzle in graph['puzzles']:
            rotation = (puzzle['rotation'] + nodes - a_rotation) % nodes
            beads = [
                (node + nodes - a_rotation) % nodes
                for node in puzzle['beads']
            ]
            letter = letters[rotation]
            letter_puzzles[letter].append(beads)

        for rotation, order in rotation_orders.items():
            rotation = (int(rotation) + nodes - a_rotation) % nodes
            letter = letters[rotation]
            puzzles = letter_puzzles[letter]
            for i, j in enumerate(order):
                puzzles.insert(i, puzzles.pop(j))

        for letter in letters[:nodes]:
            if not letter_puzzles[letter]:
                del letter_puzzles[letter]

        graph['puzzles'] = letter_puzzles

    graph['name'] = name

graphs = [
    graph for graph in graphs
    if graph['name'] is not None and not graph['name'].startswith('#')
]

# put tutorial in order
graphs[0], graphs[1] = graphs[1], graphs[0]

with open(final_path, mode='w', encoding='utf-8', newline='\n') as f:
    json.dump({'graphs': graphs}, f)

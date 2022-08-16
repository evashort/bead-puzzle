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
        with open(dst_path, mode='w', encoding='utf-8') as f:
            json.dump(difficulty, f)

        # reduce precision before sorting
        with open(dst_path, encoding='utf-8') as f:
            difficulty = json.load(f)

    graph['difficulty'] = difficulty
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

if len(sys.argv) > 1:
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

    # find easier subgraphs with higher distance because they are better
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
            graph['superior'] = [
                graph_list[j]['id'] for j in np.nonzero(superior)[0]
                if graph_list[j]['distance'] >= distance
            ]
else:
    graphs_by_id = {graph['id']: graph for graph in graphs}
    old_graphs = None
    try:
        f = open(final_path, encoding='utf-8')
    except FileNotFoundError:
        pass
    else:
        with f:
            try:
                old_graphs = json.load(f)
            except json.decoder.JSONDecodeError:
                pass

    if old_graphs is not None:
        for old_graph in old_graphs['graphs']:
            graph = graphs_by_id[old_graph['id']]
            try:
                graph['superior'] = old_graph['superior']
            except KeyError:
                pass

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

with open(names_path, mode='w', encoding='utf-8') as f:
    json.dump(id_names, f, indent=2)

for graph in graphs:
    graph['name'] = id_names[graph['id']]

graphs = [graph for graph in graphs if graph['name'] is not None]

with open(final_path, mode='w', encoding='utf-8') as f:
    json.dump({'graphs': graphs}, f)

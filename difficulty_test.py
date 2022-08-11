import collections
import json
from pathlib import Path
import random

iterations = 1000
src_folder = Path('graphs')
dst_folder = Path('src/assets/graphs')
dst_folder.mkdir(exist_ok=True)
for i, src_path in enumerate(src_folder.iterdir()):
    print(f'{i + 1} {src_path.stem}', flush=True)
    dst_path = dst_folder / src_path.name
    result = None
    try:
        f = open(dst_path, encoding='utf-8')
    except FileNotFoundError:
        pass
    else:
        with f:
            try:
                result = json.load(f)
            except json.decoder.JSONDecodeError:
                pass

    if result is None:
        with open(src_path, encoding='utf-8') as f:
            result = json.load(f)

        node_count = result['nodes']
        goal = tuple(range(1, node_count))
        total_difficulty = 0
        for i in range(iterations):
            puzzle = random.choice(result['puzzles'])
            beads = tuple(puzzle['beads'])
            hole, = set(goal + (0,)).difference(beads)
            edges = {}
            rotation = puzzle['rotation']
            for a, b in result['edges']:
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
        
        result['difficulty'] = total_difficulty / iterations
        with open(dst_path, mode='w', encoding='utf-8') as f:
            json.dump(result, f)

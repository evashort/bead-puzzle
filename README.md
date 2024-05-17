# Bead Puzzle
A circle of beads with one empty space. You can move beads into the empty space but only along certain paths. Try to get every bead into the space where it belongs: https://evashort.com/beads/

Contents:
1. [Development instructions](#development-instructions)
    1. [Recommended IDE Setup](#recommended-ide-setup)
    1. [Customize configuration](#customize-configuration)
    1. [Project Setup](#project-setup)
    1. [Compile and Hot-Reload for Development](#compile-and-hot-reload-for-development)
    1. [Compile and Minify for Production](#compile-and-minify-for-production)
1. [Generating the puzzles](#generating-the-puzzles)
    1. [Generating the graphs](#generating-the-graphs)
    1. [Interpreting the graphs](#interpreting-the-graphs)
        1. [`id` and `layout`](#id-and-layout)
        1. ["Edge length"](#edge-length)
        1. [Puzzles](#puzzles)
    1. [Generating levels](#generating-levels)

## Development instructions
This repo is based on the following template: [vitodepi16/vite-hello-world](https://github.com/vitodepi16/vite-hello-world)

These instructions are from the template.

### Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=johnsoncodehk.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=johnsoncodehk.vscode-typescript-vue-plugin).

### Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

### Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

## Generating the puzzles

### Generating the graphs
Run these steps to generate `graphs/*.json`

Normally you don't need to do this because the output is checked into the repo.

1. `pip install numpy`
1. Edit `main.py` and replace `nodes = 7` with `nodes = 3`
1. Run `main.py` to generate the following files:
    ```
    graphs/tutorial_1.json
    graphs/tutorial_2.json
    graphs/ab_ac_bc.json
    ```
1. Edit `main.py` and replace `nodes = 3` with `nodes = 4`
1. Run `main.py` to generate the following files:
    ```
    graphs/ab_ac_ad_bc_bd_cd.json
    graphs/ab_ac_ad_bc_cd.json
    graphs/ab_ad_bc_cd.json
    ```
1. Edit `main.py` and replace `nodes = 4` with `nodes = 5`
1. Run `main.py` to generate all 5-node graphs.
1. Edit `main.py` and replace `nodes = 5` with `nodes = 6`
1. Run `main.py` to generate all 6-node graphs. It will take about an hour.
1. Edit `main.py` and replace `nodes = 6` with `nodes = 7`
1. Run the following commands to generate all 7-node graphs. Open a separate console window for each command so you can run them in parallel. The commands may run for up to a week. If a command fails you can run it again and it will pick up where it left off.
    ```bash
    python main.py 6 0
    python main.py 6 1
    python main.py 6 2
    python main.py 6 3
    python main.py 6 4
    python main.py 6 5
    ```

### Interpreting the graphs

#### `id` and `layout`

To understand what `main.py` is doing, let's look at `graphs/ab_ac_ad_bc_cd.json` (a.k.a. the "Sandwich"). This graph includes the following layouts which are isomorphic to each other:
```
  A      A
 /|\    /|\
D | B  D-+-B
 \|/     |/
  C      C
```
Specifically, the second layout can be created from the first layout by swapping nodes B and C. The first layout happens to minimize the sum of all ["edge lengths"](#edge-length), so it's used as the name of the JSON file (each pair of letters is an edge).

These two layouts are represented in binary form as `101111` and `011111` respectively. Each binary digit indicates the presence or an absence of an edge as shown in the following diagram. The digits are arranged into an upper triangular matrix in *row-major order* with the *least-significant digit first*:
```
           ABCD
          A 111
101111 -> B  10
          C   1
          D

           ABCD
          A 111
011111 -> B  11
          C   0
          D
```

The general pattern is like this (note the little-endian byte order):
```
                     1247b
                      358c
87654321 0fedcba9 ->   69d
                        ae
                         f
```

Since `011111` is the lowest possible binary representation of the graph, its base64 representation is chosen as the graph's unique `id`. `101111` is chosen as the graph's `layout` because it has the lowest total ["edge length"](#edge-length).
```python
base64.b64encode(int('011111', base=2).to_bytes(length=1, byteorder='little'))
# Result: Hw==

base64.b64encode(int('101111', base=2).to_bytes(length=1, byteorder='little'))
# Result: Lw==
```
Note: The `length` argument must be 1 for 2- to 4-node graphs and 2 for 5- to 6-node graphs.

To summarize, here is the whole process of generating `id` and `layout`:
```
The layout with minimum binary representation:
  A       ABCD
 /|\     A 111
D-+-B -> B  10 -> 011111 -> Hw== (id)
  |/     C   1
  C      D

A layout that minimizes total "edge length":
  A       ABCD
 /|\     A 111
D | B -> B  11 -> 101111 -> Lw== (layout)
 \|/     C   0
  C      D
```

Let's check the results against the contents of `graphs/ab_ac_ad_bc_cd.json`:
```json
{
    "puzzles": [
        {
            "rotation": 0,
            "start": 14
        },
        {
            "rotation": 1,
            "start": 5
        }
    ],
    "distance": 7,
    "id": "Hw==",
    "layout": "Lw=="
}
```
#### "Edge length"
We don't calculate actual edge lengths when we choose a layout. Instead we use distance around the perimiter as a rough approximation. For example in the following graph, edge AD has "length" 3 and edge BF has "length" 2.
```
   A
F--+--B
E  |  C
   D
```
Minimizing "edge length" can make graphs less tangled and more comprehensible, but it's only a starting point. Later in the puzzle generation process there's a way to customize the layout of each graph.
#### Puzzles
`distance` is the maximum distance (number of moves) between any two game states for a graph. We compute the [distance matrix](https://en.wikipedia.org/wiki/Distance_matrix) not for the graph itself but for its [state space](https://en.wikipedia.org/wiki/State_space_%28computer_science%29) graph, using repeated [min-plus matrix multiplication](https://en.wikipedia.org/wiki/Min-plus_matrix_multiplication). The state space of a 7-node graph is a 5040-node graph (7! = 5040).

The "Sandwich" graph has a maximum distance of 7, so to make the puzzles challenging we only choose start and goal states that are 7 moves apart. Here are two such puzzles (0 represents the empty space):

```
  0        0
 /|\      /|\
1 | 3 -> 3 | 1
 \|/      \|/
  2        2

  1        1
 /|\      /|\
2 | 0 -> 0 | 2
 \|/      \|/
  3        3
```
The first puzzle happens to have a goal state where the beads are in clockwise order. We can always force the goal state to be in clockwise order by "repainting" the beads, as long as we repaint the initial state to match. Therefore we don't lose anything important by eliminating puzzles whose goal states are not in clockwise order.

However, the empty space has special meaning and cannot be repainted. To get it in the topmost position we rotate the entire graph, edges and all. We do this before eliminating puzzles with non-clockwise goal states. Now we have a standard goal state for all puzzles:
```
  0        0
 /|\      /|\
1 | 3 -> 3 | 1
 \|/      \|/
  2        2

  2        0
 / \      / \
3---1 -> 3---1
 \ /      \ /
  0        2
```
The remaining puzzles are uniquely determined by an initial state and a rotation of the graph's `layout`. The first puzzle has initial state `0321` and rotation 0. The second puzzle has initial state `2103` and rotation 1 (meaning the `layout` edges are rotated one space clockwise before putting the beads in their initial position).

Finally, we encode the initial state based in its index in the sorted list of all permutations (we treat the first value of each permutation as least significant and sort the permutations in descending order):
```
0  0123
1  1023
2  0213
3  2013
4  1203
5  2103 (second puzzle)
6  0132
7  1032
8  0312
9  3012
10 1302
11 3102
12 0231
13 2031
14 0321 (first puzzle)
   ...
```

These permutation indices and rotations are stored in the `puzzles` array of `graphs/ab_ac_ad_bc_cd.json`:
```json
[
    {
        "rotation": 0,
        "start": 14
    },
    {
        "rotation": 1,
        "start": 5
    }
]
```

### Generating levels

TODO: Explain `difficulty_test.py`

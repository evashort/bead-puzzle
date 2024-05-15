# bead-puzzle

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

## Interpreting the graphs

### `id` and `layout`

To understand what `main.py` is doing, let's look at `graphs/ab_ac_ad_bc_cd.json` (a.k.a. the "Sandwich"). This graph includes the following layouts which are isomorphic to each other:
```
  A     A
 /|\   /|\
D | B D-+-B
 \|/    |/
  C     C
```
Specifically, the second layout can be created from the first layout by swapping nodes B and C. The first layout happens to minimize the sum of all ["edge lengths"](#edge-length), so that layout is used as the name of the JSON file (each pair of letters is an edge).

These two layouts are represented in binary form as `101111` and `011111` respectively. Each binary digit indicates the presence or an absence of an edge as shown in the following diagram. The digits are arranged into a triangle with the *least significant digit first*:
```
A      A
B 1    B 1
C 11   C 11
D 101  D 110
  ABCD   ABCD
```

Since `011111` is the lowest possible binary representation for this graph, its base64 representation is chosen as the graph's `id`. The other binary representation is chosen as the graph's `layout` because it has the lowest total ["edge length"](#edge-length).
```python
# length is the number of bytes including leading zeros.
# 2 to 4 nodes: length=1
# 5 to 6 nodes: length=2
# 7 nodes: length=3

base64.b64encode(int('011111', base=2).to_bytes(length=1, byteorder='little'))
# Result: Hw==

base64.b64encode(int('101111', base=2).to_bytes(length=1, byteorder='little'))
# Result: Lw==
```
Let's check this against the contents of `graphs/ab_ac_ad_bc_cd.json`:
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
### "Edge length"
Instead of calculating actual edge lengths we use distance around the perimiter as a rough approximation. For example in the following graph, edge AD has "length" 3 and edge BF has "length" 2.
```
   A
F--+--B
E  |  C
   D
```

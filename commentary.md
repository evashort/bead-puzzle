"Number of moves without thinking ahead" is calculated by a computer solving the puzzle 1,000 times. The computer tries to avoid moves that put it back where it was before, but otherwise it moves randomly.

In discrete math, a group of dots connected by lines is called a [graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)). The dots are called vertices and the lines are called edges. Each puzzle in this game is based on a different graph.

I wrote a program to generate every [connected](https://en.wikipedia.org/wiki/Connectivity_%28graph_theory%29) graph with at most 7 vertices and no [leaves](https://en.wikipedia.org/wiki/Tree_(graph_theory)) (no dead ends). It generated
- 1 graph with 3 vertices
- 3 graphs with 4 vertices
- 11 graphs with 5 vertices
- 61 graphs with 6 vertices
- 507 graphs with 7 vertices

I removed most of the graphs because I thought they would make boring or repetitive puzzles.

I realized I could make every puzzle have the same goal state just by swapping the bead colors and rotating the puzzle.

[Graph isomorphism](https://en.wikipedia.org/wiki/Graph_isomorphism) has not been solved in [polynomial time](https://en.wikipedia.org/wiki/P_(complexity)). In other words, there's no efficient way to check if two graphs have the same structure. Fortunately, these graphs are small enough that removing duplicates didn't take much computing power.

My program tries to arrange the vertices to keep the edges short, but sometimes it makes the graph structure unclear. I had to manually adjust the layout of this graph.

Nautilus: For some reason, this is the only puzzle with a state space containing less than half the possible bead arrangements (1/6 of them to be exact). It has 2 cycles of length 5 and one of length 6.

# Save your progress
The following information will be saved on your device as a cookie:
1. Which puzzles you solved
1. The state of unfinished puzzles
1. The last puzzle you worked on
1. Settings you changed

No other information will be saved. You can delete the cookie or copy it to another device in Settings.

<button>Accept cookies and save</button>
<button>Don't save my progress</button>

Your progress will be saved automatically from now on.

Your progress will not be saved. You can change this in Settings.

# Save file format

1. 16-bit version
1. 16-bit settings length
1. 8-bit number of settings
    1. 8-bit setting type
1. settings
1. 32-bit last-played level ID
1. 16-bit number of variations
    1. 32-bit level ID
    1. 16-bit permutation
    1. 16-bit original bead locations
1. 16-bit number of started variations
    1. 16-bit current bead locations
    1. 8-bit history length
    1. 4-bit history[0]
    1. 4-bit tail
    1. 16-bit history[1:-1]
1. 16-bit number of won variations
1. 32-bit CRC checksum

for each won level: 32+16+16 = 64 bits = 11 characters
for each started level: 32+16+16+16+8+4+4+16 = 112 bits = 19 characters

## graphs.json
```json
{
    "graphs": [
        {
            "id": "DoA=",
            "distance": 4,
            "difficulty": 4.0,
            "states": 5,
            "layout": 58,
            "puzzles": [
                [21, 42, 79],
                [],
                [],
                []
            ]
        }
    ]
}
```

## Reductions

Levels that reduce to other levels (old number of moves -> new number)
- sandwich -> triangle (6 -> 3)
- bow tie -> sandwich (9 -> 7)
- roadblock -> bowtie (12 -> 9)
- bird base -> bowtie (13 -> 9)
- treasure chest -> bowtie (15 -> 9)
- parachute -> bird base (15 -> 13)
- sun -> treasure chest (18 -> 15)

- fox -> square (8 -> 6)
- cube -> fox (10 -> 8)
- frog base -> fox (12 -> 8)
- sand timer -> fox (15 -> 8)
- lighthouse -> cube (12 -> 10)
- cootie catcher -> frog base (14 -> 12)
- anarchy symbol -> sand timer (14 -> 15)
- hmmm -> sand timer (20 -> 15)
- raccoon -> sand timer (18 -> 15)
- coffin -> sand timer (18 -> 15)
- radioactive -> sand timer (23 -> 15)

- star -> pot (13 -> 18)
- mountain -> pot (19 -> 1)
- pocket calculator -> pot (19 -> 18)
- party cat -> star (15 -> 13)
- closed eye -> mountain (21 -> 19)
- tiara cat -> star (15 -> 13)
- coffee cup -> pocket calculator (21 -> 19)
- clam -> mountain (21 -> 19)
- barn -> mountain (22 -> 19)

- broken heart -> prohibited (20 -> 21)
- cupid's arrow -> prohibited (23 -> 21)

- open eye -> finish line (27 -> 26)
- railroad crossing sign -> finish line (24 -> 26)
- mask -> finish line (29 -> 26)
- pen nib -> finish line (24 -> 26)

Level that don't reduce: triangle, square, pot, prohibited, finish line, baseball field, heart, sundial, ferris wheel, acorn

sandwich
bow tie
cube
frog base
bridge
bird base
roadblock
anarchy symbol

🔄 loops:
pot
umbrella
cQ0=
pocket calculator
T-shirt

🪆 recursion:
square
fox
sand timer
raccoon
hmmm (as d20)
...
prohibited
cupid's arrow flipped and called broken heart

finish line
baseball field
heart
sundial
ferris wheel
acorn

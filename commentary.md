Each rotation of the puzzle has a different solution with the same number of moves. There's no reason to solve all the rotations, but they add replay value.

This is the last puzzle that has a [loop going all the way around](https://en.wikipedia.org/wiki/Hamiltonian_path) and a shortcut that skips one space. Once you find a strategy for solving this puzzle, other puzzles like it become boring, so I removed them. TODO: remove Croissant.

Every puzzle starts as far from the goal as possible, so restarting will never get you closer to winning.

"Number of moves without thinking ahead" is calculated by a computer solving the puzzle 1,000 times. The computer tries to avoid moves that put it back where it was before, but otherwise it moves randomly.

In this game, a *state* is an arrangement of beads. The [state space](https://en.wikipedia.org/wiki/State_space) is the set of all possible ways to arrange the beads while playing the game. In this puzzle, there are [6! = 720](https://en.wikipedia.org/wiki/Factorial) ways to [arrange](https://en.wikipedia.org/wiki/Permutation) the beads, but only half of them can occur while playing, so the state space size is 360.

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

I've noticed that puzzles with a state space containing exactly half the possible bead arrangements have only even-length [cycles](https://en.wikipedia.org/wiki/Cycle_%28graph_theory%29) (loops).

Nautilus: For some reason, this is the only puzzle with a state space containing less than half the possible bead arrangements (1/6 of them to be exact). It has 2 cycles of length 5 and one of length 6.

# Save your progress
The following information will be saved on your device as a cookie:
1. Which puzzles you solved
1. The state of unfinished puzzles
1. The last puzzle you worked on
1. Settings you changed

No other information will be saved. You can delete the cookie or copy it to another device in Settings.
<button>Accept cookies and save</button>

<input type="checkbox"/> Don't show this again

def from_index(index, out=None):
    if out is None:
        out = []

    if isinstance(out, int):
        out = [0] * out

    n = 0
    while index > 0 or n <= 0:
        index, remainder = divmod(index, n + 1)
        new_value = n - remainder
        for i in range(n):
            out[i] += out[i] >= new_value

        if n >= len(out):
            out.append(new_value)
        else:
            out[n] = new_value

        n += 1

    for i in range(n, len(out)):
        out[i] = i

    return out

def to_index(permutation):
    permutation = list(permutation)
    index = 0
    for i in range(len(permutation) - 1, -1, -1):
        index *= i + 1
        value = permutation[i]
        index += i - value
        for j in range(i):
            permutation[j] -= permutation[j] >= value

    return index

if __name__ == '__main__':
    import itertools
    assert [
        tuple(from_index(i, out=[0]*4)) for i in range(24)
    ] == [
        i[::-1] for i in itertools.permutations(range(3, -1, -1))
    ]

    assert all(
        to_index(from_index(i)) == i for i in range(24)
    )

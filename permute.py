import numpy as np

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

    return int(index)

def invert(permutation):
    inverse = np.zeros(len(permutation), dtype=int)
    inverse[permutation] = np.arange(len(permutation))
    return inverse

def matrix_pair_to_index(src, dst):
    permutation = np.zeros(len(src), dtype=int)
    for i in range(np.math.factorial(len(src))):
        from_index(i, out=permutation)
        result = src[:, permutation][permutation, :]
        if np.all(result == dst):
            return i
    
    raise ValueError('the matricies are not permutations of each other')

def rotate_index(index, distance, length):
    iterations = (length - distance) % length
    for _ in range(iterations):
        index = rotate_left(index, length)

    return index

def rotate_left(index, length):
    factorial = 1 # factorial of n - 1
    for n in range(1, length):
        j = index // factorial % ((n + 1) * n)
        offset = n + j * (n - 1) + (j // (n + 1) - j // n * n) * (n + 1)
        index += offset * factorial
        factorial *= n

    return index

# you can get there by swapping pairs
# 0123 -> 1023 -> 1203 -> 1230

# swap first two = i + 1 - 2 * (i % 2)

# swap second two = [2,3,-2,2,-3,-2][i % 6]
# i = np.arange(6)
# 2 + 1 * (i % 2 - 4 * (i // 2) + 3 * (i // 3))
# 2! + i % 2 - 2*2! * (i // 2) + (2! + 1!) * (i // 3)

# swap third two = [6,10,14,-6,6,10,-10,-6,6,-14,-10,-6][i // 2 % 12]
# i = np.arange(24)
# 6 + 4 * (i % 6 // 2) - 12 * (i // 6) + 8 * (i // 8)
# 6 + 4 * (i//2 % 3 - 3 * (i//2 // 3) + 2 * (i//2 // 4))
# 3! + 2*2! * (i//2! % 3) - 2*3! * (i//2! // 3) + 4*2! * (i//2! // 4))
# n! + (n-1)*(n-1)! * (i//(n-1)! % n) - 2*n! * (i//(n-1)! // n) + (n+1)*(n-1)! * (i//(n-1)! // (n + 1))
# math.factorial(n) + i // math.factorial(n-1) % n * math.factorial(n-1) * (n-1) - i // math.factorial(n-1) // n * 2 * math.factorial(n) + i // (n+1) // math.factorial(n-1) * (n+1) * math.factorial(n-1)
# math.factorial(n-1) * (n + i//math.factorial(n-1) % n * (n-1) - i//math.factorial(n-1) // n * n * 2 + i//math.factorial(n-1) // (n+1) * (n+1))
# j = i // math.factorial(n-1)
# math.factorial(n-1) * (n + j % n * (n-1) - j // n * n * 2 + j // (n+1) * (n+1))
# math.factorial(n-1) * (n + j * (n-1) - j // n * n * (n-1) - j // n * n * 2 + j // (n+1) * (n+1))
# math.factorial(n-1) * (n + j * (n-1) - j // n * n * (n+1) + j // (n+1) * (n+1))
# math.factorial(n-1) * (n + j * (n-1) + (j // (n+1) - j // n * n) * (n+1))

# swap second and fourth = [14, 19,  6, 19,  6, 11,  6, 11, -6, 14, -6,  6, -6,  6,-14,  6,-11, -6,-11, -6,-19, -6,-19,-14]
#                        = [12, 18,  6, 18,  6, 12,  6, 12, -6, 12, -6,  6, -6,  6,-12,  6,-12, -6,-12, -6,-18, -6,-18,-12]
#                        + [ 2,  1,  0,  1,  0, -1,  0, -1,  0,  2,  0,  0,  0,  0, -2,  0,  1,  0,  1,  0, -1,  0, -1, -2]
# = [2,  3,  1,  3,  1,  2,  1,  2, -1,  2, -1,  1, -1,  1, -2,  1, -2, -1, -2, -1, -3, -1, -3, -2] * 6
# + [2,  1,  0,  1,  0, -1,  0, -1,  0,  2,  0,  0,  0,  0, -2,  0,  1,  0,  1,  0, -1,  0, -1, -2]
# = ((i + i // 3 + 1) % 3 + 1 - 4 * (((i + 1) % 2 + i // 8 + 1) // 3)) * 6 +
# + (2 * (i // 8) + 2 + (i % 2 + i // 8 + 1) // 3 - i % 3 - i // 3) =
# = 6 * ((i + i // 3 + 1) % 3) + 8 - 24 * (((i + 1) % 2 + i // 8 + 1) // 3) + 2 * (i // 8) + (i % 2 + i // 8 + 1) // 3 - i % 3 - i // 3
# = 6 * ((i + i // 3 + 1) % 3) + 8 + 3 * (i // 8) - 25 * ((i // 8 + 2 - i % 2) // 3) - i + 2 * (i // 3)
# = 6 * (i + i // 3 + 1) - 18 * ((i + i // 3 + 1) // 3) + 8 + 3 * (i // 8) - 25 * ((2 - i % 2 + i // 8) // 3) - i + 2 * (i // 3)
# = 5 * i + 8 * (i // 3) - 18 * ((i + i // 3 + 1) // 3) + 14 + 3 * (i // 8) - 25 * ((2 - i % 2 + i // 8) // 3)
# = 5 * i + 8 * (i // 3) - 18 * ((i - i // 8) // 2) + 14 + 3 * (i // 8) - 25 * ((2 - i % 2 + i // 8) // 3)

def find_zero(index):
    result = 0
    n = 1
    while index > 0:
        if index % (n + 1) == n:
            result = n

        n += 1
        index //= n
    
    return result

def find_value(index, value):
    unit = 1
    n = 1
    while unit <= index:
        n += 1
        unit *= n

    while n > value:
        unit //= n
        quantity = index // unit
        index %= unit
        n -= 1
        if quantity == n - value:
            return n
        elif quantity > n - value:
            value -= 1
    
    return value

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

    assert from_index(rotate_left(to_index((2, 1, 4, 0, 3)), 5), 5) \
        == [1, 4, 0, 3, 2]
    
    assert find_zero(to_index((2, 1, 4, 0, 3))) == 3

    assert [find_value(to_index((2, 1, 4, 0, 3)), i) for i in range(5)] == [3, 1, 0, 4, 2]

    assert [[find_value(i, j) for j in range(4)] for i in range(24)] == [
        [0, 1, 2, 3],
        [1, 0, 2, 3],
        [0, 2, 1, 3],
        [1, 2, 0, 3],
        [2, 0, 1, 3],
        [2, 1, 0, 3],
        [0, 1, 3, 2],
        [1, 0, 3, 2],
        [0, 2, 3, 1],
        [1, 2, 3, 0],
        [2, 0, 3, 1],
        [2, 1, 3, 0],
        [0, 3, 1, 2],
        [1, 3, 0, 2],
        [0, 3, 2, 1],
        [1, 3, 2, 0],
        [2, 3, 0, 1],
        [2, 3, 1, 0],
        [3, 0, 1, 2],
        [3, 1, 0, 2],
        [3, 0, 2, 1],
        [3, 1, 2, 0],
        [3, 2, 0, 1],
        [3, 2, 1, 0],
    ]

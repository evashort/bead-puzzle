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

def swap1(index, n):
    f = np.math.factorial(n)
    g = f * (n+1)
    h = g * (n+2)
    i = index // f
    j = i // (n+1)
    k = j // (n+2)
    ii = i * f
    jj = j * g
    kk = k * h
    return index + kk + g + i * g - j * h - ii % (g + f)

def swap2(index, n):
    f = np.math.factorial(n)
    g = f * (n+1)
    h = g * (n+2)
    x = h * (n+3)
    i = index // f
    j = i // (n+1)
    k = j // (n+2)
    l = k // (n+3)
    ii = i * f
    jj = j * g
    kk = k * h
    ll = l * x
    return index + l * (h + x) + g + 2 * h - ii \
        + i * g // h * (g + h) \
        + j * h // x * (g - h) \
        + (i * g - j * h) * (n+2) \
        + (i + (j // (n+3) - j) * (n+1)) // (n+2) * (h + f)

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

# swap first and fourth = [21, 14, 21,  6, 13,  6, 13,  6, 14, -6,  6, -6,  6, -6,  6,-14, -6,-13, -6,-13, -6,-21,-14,-21]
#                   = 6 * [ 3,  2,  3,  1,  2,  1,  2,  1,  2, -1,  1, -1,  1, -1,  1, -2, -1, -2, -1, -2, -1, -3, -2, -3]
#                       + [ 3,  2,  3,  0,  1,  0,  1,  0,  2,  0,  0,  0,  0,  0,  0, -2,  0, -1,  0, -1,  0, -3, -2, -3]
# = 6 * (3 - i % 2 + (2 - i % 2 + i // 8) // 3 - (i + 3 + 6 * (i // 8)) // 6)
# + 3 - i % 2 - (2 - i % 2 + i // 8) // 3 - (i + 3 + 6 * (i // 8)) // 6 * 2 + i // 8 * 4
# = 21 - i % 2 * 7 + (2 - i % 2 + i // 8) // 3 * 5 - (i + 3 + 6 * (i // 8)) // 6 * 8 + i // 8 * 4

# swap 3rd and 5th
# = [ 54,  76,  98,  24,  76,  98,  24,  46,  98,  24,  46,  68,
#     24,  46,  68, -24,  54,  76, -24,  24,  76, -24,  24,  46,
#    -24,  24,  46, -54,  24,  46, -46, -24,  54, -46, -24,  24,
#    -46, -24,  24, -76, -24,  24, -76, -54,  24, -68, -46, -24,
#    -68, -46, -24, -98, -46, -24, -98, -76, -24, -98, -76, -54][i // 2]
# = 24 * [ 2, 3, 4, 1, 3, 4, 1, 2, 4, 1, 2, 3,
#          1, 2, 3,-1, 2, 3,-1, 1, 3,-1, 1, 2,
#         -1, 1, 2,-2, 1, 2,-2,-1, 2,-2,-1, 1,
#         -2,-1, 1,-3,-1, 1,-3,-2, 1,-3,-2,-1,
#         -3,-2,-1,-4,-2,-1,-4,-3,-1,-4,-3,-2]
#  + 2 * [ 3, 2, 1, 0, 2, 1, 0,-1, 1, 0,-1,-2,
#          0,-1,-2, 0, 3, 2, 0, 0, 2, 0, 0,-1,
#          0, 0,-1,-3, 0,-1, 1, 0, 3, 1, 0, 0,
#          1, 0, 0,-2, 0, 0,-2,-3, 0, 2, 1, 0,
#          2, 1, 0,-1, 1, 0,-1,-2, 0,-1,-2,-3]
# = 24 * (2 + i % 3 - i // 3 + i // 4 - (i // 15 + 2 - i % 3) // 3)
#  + 2 * (3 - i % 3 - i // 3 * 3 + i // 4 * 3 - (i // 15 + 2 - i % 3) // 3 + i // 15 * 4)
# = 54 + i % 3 * 22 - i // 3 * 30 + i // 4 * 30 - (i // 15 + 2 - i % 3) // 3 * 26 + i // 15 * 8
# = 54 + i * 22 - i // 3 * 96 + i // 4 * 30 - (i // 15 + 2 - i % 3) // 3 * 26 + i // 15 * 8

# swap 2nd and 5th
# =  [  80, 103,  54, 103,  54,  77,  80, 103,  24, 103,  24,  77,
#       50, 103,  24, 103,  24,  47,  50,  73,  24,  73,  24,  47,
#       50,  73,  24,  73,  24,  47,  54,  77, -24,  80, -24,  54,
#       24,  77, -24,  80, -24,  24,  24,  47, -24,  50, -24,  24,
#       24,  47, -24,  50, -24,  24,  24,  47, -54,  50, -54,  24,
#      -24,  54, -50,  54, -47, -24, -24,  24, -50,  24, -47, -24,
#      -24,  24, -50,  24, -47, -24, -24,  24, -80,  24, -77, -24,
#      -54,  24, -80,  24, -77, -54, -47, -24, -73, -24, -73, -50,
#      -47, -24, -73, -24, -73, -50, -47, -24,-103, -24,-103, -50,
#      -77, -24,-103, -24,-103, -80, -77, -54,-103, -54,-103, -80]
# = 24 * [ 3, 4, 2, 4, 2, 3, 3, 4, 1, 4, 1, 3, 2, 4, 1, 4, 1, 2, 2, 3, 1, 3, 1, 2,
#          2, 3, 1, 3, 1, 2, 2, 3,-1, 3,-1, 2, 1, 3,-1, 3,-1, 1, 1, 2,-1, 2,-1, 1,
#          1, 2,-1, 2,-1, 1, 1, 2,-2, 2,-2, 1,-1, 2,-2, 2,-2,-1,-1, 1,-2, 1,-2,-1,
#         -1, 1,-2, 1,-2,-1,-1, 1,-3, 1,-3,-1,-2, 1,-3, 1,-3,-2,-2,-1,-3,-1,-3,-2,
#         -2,-1,-3,-1,-3,-2,-2,-1,-4,-1,-4,-2,-3,-1,-4,-1,-4,-3,-3,-2,-4,-2,-4,-3]
#      + [ 8, 7, 6, 7, 6, 5, 8, 7, 0, 7, 0, 5, 2, 7, 0, 7, 0,-1, 2, 1, 0, 1, 0,-1,
#          2, 1, 0, 1, 0,-1, 6, 5, 0, 8, 0, 6, 0, 5, 0, 8, 0, 0, 0,-1, 0, 2, 0, 0,
#          0,-1, 0, 2, 0, 0, 0,-1,-6, 2,-6, 0, 0, 6,-2, 6, 1, 0, 0, 0,-2, 0, 1, 0,
#          0, 0,-2, 0, 1, 0, 0, 0,-8, 0,-5, 0,-6, 0,-8, 0,-5,-6, 1, 0,-1, 0,-1,-2,
#          1, 0,-1, 0,-1,-2, 1, 0,-7, 0,-7,-2,-5, 0,-7, 0,-7,-8,-5,-6,-7,-6,-7,-8]
# = 24 * (2 + (i % 6 + 1 + i % 6 // 3) % 3 - (2 - i % 2 + i // 8) // 3 - ((i // 30 * 2 + i // 2 % 3) // 3 + 1 - i % 2) // 2)
# + 8 - i % 6 + i % 6 // 3 * 2 - (2 - i % 2 + i // 8) // 3 * 6 + i // 30 * 4 + ((i // 30 * 2 + i // 2 % 3) // 3 * 5 + i % 2) // 2
# = 56 - i % 6 + i % 6 // 3 * 2 + (i % 6 + 1 + i % 6 // 3) % 3 * 24 - (2 - i % 2 + i // 8) // 3 * 30 + i // 30 * 4 + ((i // 30 * 2 + i // 2 % 3) // 3 * 2 + i % 2) // 3 * 25 - (i // 30 * 2 + i // 2 % 3) // 3 * 22
#
# ((i // 30 * 2 + i // 2 % 3) // 3 * 5 + i % 2) // 2 - 24 * (((i // 30 * 2 + i // 2 % 3) // 3 + 1 - i % 2) // 2)
# == (i // 30 * 2 + i // 2 % 3) // 3 * 3 - ((i // 30 * 2 + i // 2 % 3) // 3 * 2 + 1 - i % 2) // 3 * 25
# == ((i // 30 * 2 + i // 2 % 3) // 3 * 2 + i % 2) // 3 * 25 - (i // 30 * 2 + i // 2 % 3) // 3 * 22

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
    import random
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

    random.seed("first arbitrary string that stays the same every time but can be changed if needed")
    for i in range(10000):
        index = random.randrange(10000)
        n = random.randrange(25)
        actual = swap1(index, n)
        permutation = from_index(index, n + 2)
        permutation[n], permutation[n + 1] = permutation[n + 1], permutation[n]
        expected = to_index(permutation)
        assert actual == expected

    assert from_index(swap2(to_index([5, 0, 3, 4, 2, 1]), 3), 6) == [5, 0, 3, 1, 2, 4]
    assert from_index(swap2(to_index([5, 0, 4, 3, 6, 2, 1]), 4), 7) == [5, 0, 4, 3, 1, 2, 6]
    assert from_index(swap2(to_index([6, 1, 4, 5, 3, 2, 0]), 3), 7) == [6, 1, 4, 2, 3, 5, 0]
    random.seed("an arbitrary string that stays the same every time but can be changed if needed")
    for i in range(100000):
        index = random.randrange(100000)
        n = random.randrange(25)
        actual = swap2(index, n)
        permutation = from_index(index, n + 3)
        permutation[n], permutation[n + 2] = permutation[n + 2], permutation[n]
        expected = to_index(permutation)
        assert actual == expected

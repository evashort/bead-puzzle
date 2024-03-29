import numpy as np

def get_value(index, position):
    n = 0
    result = position
    while index > 0:
        index, remainder = divmod(index, n + 1)
        if (n == position):
            result = n - remainder
        elif n > position:
            result += result >= n - remainder

        n += 1

    return result

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

def swap_in_index(index, start, end):
    if end < start:
        start, end = end, start

    stop = end + 1

    unit = 1
    for n in range(start):
        unit *= n + 1

    index, fraction = divmod(index, unit)
    out = [0] * (stop - start)
    for n in range(start, stop):
        index, remainder = divmod(index, n + 1)
        value = n - remainder
        for i in range(n - start):
            out[i] += out[i] >= value
        
        out[n - start] = value

    out[0], out[-1] = out[-1], out[0]

    for n in range(stop - 1, start - 1, -1):
        index *= n + 1
        value = out[n - start]
        index += n - value
        for i in range(n - start):
            out[i] -= out[i] >= value

    index *= unit
    index += fraction

    return index

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

def matrix_pair_to_indices(src, dst):
    permutation = np.zeros(len(src), dtype=int)
    for i in range(np.math.factorial(len(src))):
        from_index(i, out=permutation)
        result = src[:, permutation][permutation, :]
        if np.all(result == dst):
            yield i

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

def swap0(index, n):
    # for n=2: 4 + no_diagonal(i, 2)
    # for n=3: 18 + no_diagonal(i // 2, 3) * 2 + no_diagonal(expand(i // 2, 3) * 2 + i % 2, 2)
    # for n=4: 96 + no_diagonal(i // 6, 4) * 6 + no_diagonal(expand(i // 6, 4) * 3 + i // 2 % 3, 3) * 2 + no_diagonal(expand(expand(i // 6, 4) * 3 + i // 2 % 3, 3) * 2 + i % 2, 2)

    factorial = 1
    for i in range(n):
        factorial *= i + 1

    result, index = divmod(index, factorial * (n+1))
    result *= factorial * (n+1)

    # start with minimum length-n permutation that ends with zero
    result += factorial * n

    digit = 0
    for i in range(n, 1, -1):
        factorial //= i
        digit += index // factorial
        result += no_diagonal(digit, i) * factorial
        digit = expand(digit, i)
        digit *= i - 1
        index %= factorial

    return result

def no_diagonal(i, n):
    '''
    no_diagonal(i, 5) = 12340
                        02341
                        01342
                        01243
                        01234
                        01234
	'''
    return (1 + i + i // (n+1)) % (n+1) - i % n // (n-1) * (n - i // n)

def expand(i, n):
    '''
    expand(i, 4) = 0003
                   0113
                   1123
                   2223
                   3333
	'''
    return i // (n+1) + i % n // (n-1) * (n-1 - i // (n+1))

def swap0real(index, n):
    permutation = from_index(index, n+1)
    z = permutation.index(0)
    permutation[z] = permutation[n]
    permutation[n] = 0
    return to_index(permutation)

print([swap0real(i, 0) - (i + 1) // 3 % 2 * 2 - i // 6 * 6 - np.array([0]*18+[-6,-12,-6,-20,-12,-16])[i % 24] for i in range(120)])
i = np.arange(24)
np.array([-24, -48, -24, -74, -48, -70, -24, -48, -24, -104, -48, -100, -24, -78, -24, -104, -78, -100, -48, -66, -48, -84, -66, -84]) + 24 * (i % 2 + i // 3 % 2 + (i // 8 + i % 2) // 2 + 1)
np.array([-6,-12,-6,-20,-12,-16]) + np.arange(6) % 2 * 6 + np.arange(6) // 3 * 6 + 6

print([swap0real(i, 0) - (i + 1) // 3 % 2 * 2 - i // 6 * 6 + i // 6 % 4 // 3 * 6 * (i % 2 + i % 6 // 3 + 1) + i // 24 % 5 // 4 * 24 * (i % 2 + i % 24 // 3 % 2 + (i % 24 // 8 + i % 2) // 2 + 1) + i // 120 % 6 // 5 * 120 * (i % 2 + i // 3 % 2 + 1 + (i % 24 // 8 + i % 2) // 2 + i % 3 % 2 * (i % 120 // 60) + (i % 120 + 45) // 75 % 2 * (i % 6 // 3) * (i % 2) + i % 120 // 90 * ((i + 3) % 6 // 3) * ((i + 1) % 2)) for i in range(720)])
i = np.arange(120)
np.array([-120, -240, -120, -362, -240, -358, -120, -240, -120, -488, -240, -484, -120, -366, -120, -488, -366, -484, -240, -354, -240, -470, -354, -466, -120, -240, -120, -362, -240, -358, -120, -240, -120, -632, -240, -628, -120, -366, -120, -632, -366, -628, -240, -354, -240, -614, -354, -610, -120, -240, -120, -506, -240, -502, -120, -240, -120, -632, -240, -628, -120, -510, -120, -632, -510, -628, -240, -498, -240, -614, -498, -610, -120, -384, -120, -506, -384, -502, -120, -384, -120, -632, -384, -628, -120, -510, -120, -632, -510, -628, -384, -498, -384, -614, -498, -610, -240, -336, -240, -434, -336, -430, -240, -336, -240, -536, -336, -532, -240, -438, -240, -536, -438, -532, -336, -426, -336, -518, -426, -514]) + 120 * (i % 2 + i // 3 % 2 + 1 + (i % 24 // 8 + i % 2) // 2 + i % 3 % 2 * (i % 120 // 60) + (i % 120 + 45) // 75 % 2 * (i % 6 // 3) * (i % 2) + i % 120 // 90 * ((i + 3) % 6 // 3) * ((i + 1) % 2))

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
        get_value(i, 3) for i in range(120)
    ] == [
        i[::-1][3] for i in itertools.permutations(range(4, -1, -1))
    ]

    assert [
        tuple(from_index(i, out=[0]*4)) for i in range(24)
    ] == [
        i[::-1] for i in itertools.permutations(range(3, -1, -1))
    ]

    assert all(
        to_index(from_index(i)) == i for i in range(24)
    )

    assert from_index(swap_in_index(to_index([3, 2, 6, 5, 1, 0, 4, 8, 7]), 2, 7)) \
        == [3, 2, 8, 5, 1, 0, 4, 6, 7]

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

    for n in range(0, 6):
        for i in range(min(n+1, 3) * np.math.factorial(n+1)):
            assert swap0real(i, n) == swap0(i, n)

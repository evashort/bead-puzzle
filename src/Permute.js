export function getValue(index, position) {
    let result = position
    for (let n = 0; index > 0; n++) {
        let remainder = index % (n + 1)
        index -= remainder
        index /= n + 1
        if (n == position) {
            result = n - remainder
        } else if (n > position) {
            result += result >= n - remainder
        }
    }

    return result
}

export function fromIndex(index, length) {
    let out = new Array(length)
    let n = 0
    for (; index > 0 || n <= 0; n++) {
        let remainder = index % (n + 1)
        index -= remainder
        index /= n + 1
        let value = n - remainder
        for (let i = 0; i < n; i++) {
            out[i] += out[i] >= value
        }

        out[n] = value
    }

    for (; n < length; n++) {
        out[n] = n
    }

    return out
}

export function swap(index, a, b) {
    if (b < a) {
        [a, b] = [b, a]
    }

    let a_factorial = 1
    for (let n = 1; n <= a; n++) {
        a_factorial *= n
    }

    let backup = index % a_factorial
    index -= backup
    index /= a_factorial

    let out = new Array(b + 1 - a)
    for (let n = a; n <= b; n++) {
        let remainder = index % (n + 1)
        index -= remainder
        index /= n + 1
        let value = n - remainder
        for (let i = 0; i < n - a; i++) {
            out[i] += out[i] >= value
        }

        out[n - a] = value
    }

    [out[0], out[out.length - 1]] = [out[out.length - 1], out[0]]

    for (let n = b; n >= a; n--) {
        index *= n + 1
        let value = out[n - a]
        index += n - value
        for (let i = 0; i < n - a; i++) {
            out[i] -= out[i] >= value
        }
    }

    index *= a_factorial
    index += backup
    return index
}

export function findZero(index) {
    let result = 0
    let n = 1
    while (index > 0) {
        let remainder = index % (n + 1)
        if (remainder == n) {
            result = n
        }

        n++
        index -= remainder
        index /= n
    }
    
    return result
}

export function findValue(index, value) {
    let unit = 1
    let n = 1
    while (unit <= index) {
        n++
        unit *= n
    }

    while (n > value) {
        unit /= n
        let remainder = index % unit
        let quantity = (index - remainder) / unit
        index = remainder
        n--
        if (quantity == n - value) {
            return n
        } else if (quantity > n - value) {
            value--
        }
    }
    
    return value
}

export function rotateRight(index, distance, length) {
    let iterations = ((-distance % length) + length) % length
    for (; iterations > 0; iterations--) {
        index = rotateLeftOnce(index, length)
    }

    return index
}

function rotateLeftOnce(index, length) {
    let factorial = 1 // factorial of n - 1
    for (let n = 1; n < length; n++) {
        let remainder = index % factorial
        let j = (index - remainder) / factorial % ((n + 1) * n)
        let offset = n + j * n - j % (n + 1) - (j - j % n) * (n + 1)
        index += offset * factorial
        factorial *= n
    }

    return index
}

var Permute = {
    getValue: getValue,
    fromIndex: fromIndex,
    findZero: findZero,
    findValue: findValue,
    swap: swap,
    rotateRight: rotateRight,
}

export default Permute

export function fromIndex(index, length) {
    let out = new Array(length)
    let n = 0
    for (; index > 0 || n <= 0; n++) {
        let remainder = index % (n + 1)
        index -= remainder
        index /= n + 1
        let newValue = n - remainder
        for (let i = 0; i < n; i++) {
            out[i] += out[i] >= newValue
        }

        out[n] = newValue
    }

    for (; n < length; n++) {
        out[n] = n
    }

    return out
}

export function findZero(index) {
    let result = 0
    let n = 1
    while (index > 0) {
        let remainder = index % (n + 1)
        if (remainder == n) {
            result = n
        }

        n += 1
        index -= remainder
        index /= n
    }
    
    return result
}

var Permute = {
    fromIndex: fromIndex,
    findZero: findZero,
}

export default Permute

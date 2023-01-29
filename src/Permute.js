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

var Permute = {
    fromIndex: fromIndex,
}

export default Permute

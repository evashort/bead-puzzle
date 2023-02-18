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
        remainder = index % unit
        quantity = (index - remainder) / unit
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

var Permute = {
    fromIndex: fromIndex,
    findZero: findZero,
    findValue: findValue,
}

export default Permute

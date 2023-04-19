export function bytesToNodeCount(bytes) {
    let lastIndex = bytes.length - 1
    for (; lastIndex > 0 && bytes[lastIndex] == 0; lastIndex--);
    let bitCount = 8 * lastIndex
    for (let byte = bytes[lastIndex]; byte > 0; byte >>= 1) {
        bitCount++
    }

    // https://oeis.org/A002024
    let n = Math.floor((Math.sqrt(8 * bitCount) + 1) / 2)
    return n + 1
}

export function bytesToMatrix(bytes, layout) {
    let length = layout.length
    let matrix = new Uint8Array(length * length)
    for (let b = 0; b < length; b++) {
        for (let a = 0; a < b; a++) {
            let [c, d] = [layout[a], layout[b]]
            if (d < c) {
                [c, d] = [d, c]
            }

            let bit = c + d * (d - 1) / 2
            if (bytes[bit >> 3] & (1 << (bit & 7))) {
                matrix[a + b * length] = matrix[b + a * length] = 1
            }
        }
    }

    return matrix
}

var SimpleGraph = {
    bytesToNodeCount: bytesToNodeCount,
    bytesToMatrix: bytesToMatrix,
}

export default SimpleGraph

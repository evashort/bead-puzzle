export function cubicBezier(a, b, c, d) {
    return function(t) {
        let s = 1 - t
        let e = a * s + b * t
        let f = b * s + c * t
        let g = c * s + d * t
        let h = e * s + f * t
        let i = f * s + g * t
        return h * s + i * t
    }
}

export function cubicBezierSlope(a, b, c, d) {
    // https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B%C3%A9zier_curves
    return function(t) {
        let s = 1 - t
        let e = (b - a) * s + (c - b) * t
        let f = (c - b) * s + (d - c) * t
        return 3 * (e * s + f * t)
    }
}

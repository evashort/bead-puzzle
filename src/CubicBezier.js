export default function cubicBezier(a, b, c, d) {
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

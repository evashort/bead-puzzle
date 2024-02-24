export function length(ax, ay, bx, by, cx, cy, dx, dy, error=0.1) {
    let abLength = Math.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay))
    let bcLength = Math.sqrt((cx - bx) * (cx - bx) + (cy - by) * (cy - by))
    let cdLength = Math.sqrt((dx - cx) * (dx - cx) + (dy - cy) * (dy - cy))
    let lowerBound = Math.sqrt((dx - ax) * (dx - ax) + (dy - ay) * (dy - ay))
    let upperBound = abLength + bcLength + cdLength
    if (upperBound - lowerBound < error) {
        // overestimate so the trophy rests after the bend when not pushed, so
        // it doesn't snap rotate when pushed forward
        return upperBound
    }

    let b1x = 0.5 * (ax + bx), bcx = 0.5 * (bx + cx), c2x = 0.5 * (cx + dx)
    let c1x = 0.5 * (b1x + bcx), b2x = 0.5 * (bcx + c2x)
    let d1a2x = 0.5 * (c1x + b2x)
    let b1y = 0.5 * (ay + by), bcy = 0.5 * (by + cy), c2y = 0.5 * (cy + dy)
    let c1y = 0.5 * (b1y + bcy), b2y = 0.5 * (bcy + c2y)
    let d1a2y = 0.5 * (c1y + b2y)
    let l1 = length(ax, ay, b1x, b1y, c1x, c1y, d1a2x, d1a2y, 0.5 * error)
    let l2 = length(d1a2x, d1a2y, b2x, b2y, c2x, c2y, dx, dy, 0.5 * error)
    return l1 + l2
}

export function slope(a, b, c, d, x) {
  // https://computergraphics.stackexchange.com/questions/10551/how-to-take-the-derivative-of-a-b%C3%A9zier-curve
  let r = b - a, s = c - b, t = d - c
  let y = 1 - x
  let u = y * r + x * s, v = y * s + x * t
  let w = y * u + x * v
  return 3 * w
}

export function value(a, b, c, d, x) {
  let y = 1 - x
  let e = y * a + x * b, f = y * b + x * c, g = y * c + x * d
  let h = y * e + x * f, i = y * f + x * g
  let j = y * h + x * i
  return j
}

export function estimateParameter(length, controlLength, offset) {
    // https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B%C3%A9zier_curves
    // x = A(1-t)^3 + B*3t(1-t)^2 + C*3(1-t)t^2 + D*t^3
    // A = 0, B = c/l, C = 1 - c/l, D = 1
    // x = c/l*3t(1-t)^2 + (1-c/l)*3(1-t)t^2 + t^3
    // c/l = 0: x ~= 1/2 - cos(pi*t)/2
    // c/l = 1/3: x = t
    // x = 1/2 - cos(pi*t)/2
    // cos(pi*t)/2 = 1/2 - x
    // cos(pi*t) = 1 - 2x
    // pi*t = acos(1-2x)
    // t = acos(1-2x)/pi
    // t = (1 - 3c/l)acos(1-2x)/pi + 3c/l*x
    // now we improve the approximation even more:
    /*
import numpy
from scipy import interpolate
from matplotlib import pyplot as plt
x = numpy.linspace(0, 1, 1000)
f = interpolate.CubicSpline((3 - 2 * x) * x ** 2, x)
acos = numpy.arccos(1 - 2 * x) / numpy.pi
acos_factor = 0.914 # hand-tuned
line_factor = 0.0862 # hand-tuned
t_approximation = 0.5 + acos_factor * (acos - 0.5) + line_factor * (x - 0.5)
plt.plot(x, t_approximation - f(x))
plt.title('error in t')
plt.show()
*/
    let x = offset / length
    // m = "how much does controlLength matter"
    // without this parameter, the formula assigns too much importance to
    // controlLength and the arrow heads are too far back. I decreased m
    // until none of the arrow tails stuck out in front of the arrow heads.
    let m = 0.3
    let ratio = Math.pow(3 * controlLength / length, m)
    let acos = -0.0001 + 0.0862 * x + 0.914 * Math.acos(1 - 2 * x) / Math.PI
    return (1 - ratio) * acos + ratio * x
}

var Bezier = {
    length: length,
    slope: slope,
    value: value,
    estimateParameter: estimateParameter,
}

export default Bezier

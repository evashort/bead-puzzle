export default function GetControlVector(thisX, thisY, otherX, otherY, length) {
  let otherLength = Math.sqrt(otherX * otherX + otherY * otherY)
  let thisLength = Math.sqrt(thisX * thisX + thisY * thisY)
  let dx = thisX * otherLength - otherX * thisLength
  let dy = thisY * otherLength - otherY * thisLength
  let oldLength = Math.sqrt(dx * dx + dy * dy)
  let factor = oldLength > 0 ? length / oldLength : 0
  return {x: dx * factor, y: dy * factor}
}

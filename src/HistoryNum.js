export function historyToNumber(history, size) {
    let length = history.length - 1
    let hole = history[length]
    let rejects = new Array(3)
    let num = 0
    for (let i = length - 1; i >= 0; i--) {
        num *= size - Math.min(i, 3)
        // see numberToHistory for an explanation of rejects
        rejects[0] = i >= 1 ? history[i - 1] : size
        rejects[1] = i >= 2 ? history[i - 2] : size
        rejects[2] = i >= 3 ? hole : size
        rejects.sort((a, b) => a - b)
        let value = history[i]
        value -= value >= rejects[2]
        value -= value >= rejects[1]
        value -= value >= rejects[0]
        num += value
    }

    return num
}

export function numberToHistory(num, length, size, hole) {
    let history = new Array(length + 1)
    let rejects = new Array(3)
    for (let i = 0; i < length; i++) {
        let choices = size - Math.min(i, 3)
        let value = num % choices
        num -= value
        num /= choices
        rejects[0] = i >= 1 ? history[i - 1] : size // can't repeat
        rejects[1] = i >= 2 ? history[i - 2] : size // can't go back
        // note: we don't discard hole when i == 2 because it might already be
        // eliminated by "can't go back" and we need a consistent number of
        // choices at each index
        rejects[2] = i >= 3 ? hole : size // only start can be hole
        rejects.sort((a, b) => a - b)
        value += value >= rejects[0]
        value += value >= rejects[1]
        value += value >= rejects[2]
        history[i] = value
    }

    history[length] = hole
    return history
}

/*
// fuzz testing
for (let i = 0; i < 10000; i++) {
    let size = 1 + Math.floor(Math.random() * 11)
    let length = Math.floor(Math.random() * size)
    let history = new Array(length + 1)
    for (let j = 0; j <= length; j++) {
        history[j] = Math.floor(Math.random() * size)
    }

    let skip = false
    for (let j = 0; j <= length - 1; j++) {
        if (history[j] == history[j + 1]) {
            skip = true
            break
        }
    }

    for (let j = 0; j <= length - 2; j++) {
        if (history[j] == history[j + 2]) {
            skip = true
            break
        }
    }

    for (let j = 1; j <= length - 1; j++) {
        if (history[j] == history[length]) {
            skip = true
            break
        }
    }

    if (skip) {
        i--
        continue
    }

    let num = historyToNumber(history, size)
    let newHistory = numberToHistory(num, length, size, history[length])
    if (history.toString() != newHistory.toString()) {
        console.log(size, history.toString(), num, newHistory.toString())
    }
}
*/

var HistoryNum = {
    historyToNumber: historyToNumber,
    numberToHistory: numberToHistory,
}

export default HistoryNum

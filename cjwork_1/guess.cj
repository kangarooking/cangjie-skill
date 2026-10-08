// guess.cj - 终极可运行版 (Cangjie 1.0.0.5)
import std.random.*
import std.convert.*
import std.env.*

func randInt(min: Int64, max: Int64): Int64 {
    let r = Random()
    let range = max - min + 1
    // 利用标准库 nextInt64(range) 直接生成 [0, range) 的正数，彻底避开取模/abs/转换
    return min + r.nextInt64(range)
}

func temperatureHint(diff: Int64): String {
    if (diff == 0) { return "完美命中！" }
    else if (diff <= 3) { return "非常烫！" }
    else if (diff <= 7) { return "很热！" }
    else if (diff <= 15) { return "温热" }
    else if (diff <= 30) { return "有点冷" }
    else { return "冰封千里" }
}

main() {
    println("欢迎来到 AI 猜数字挑战")
    println("我想好了一个 1 到 100 之间的数字\n")

    let target = randInt(1, 100)
    var guess: Int64 = 0
    var count: Int64 = 0
    var minDiff: Int64 = 100

    while (guess != target) {
        print("请输入你的猜测（1-100）：")
        let input = getStdIn().readln().getOrThrow()

        if (input == "") {
            println("你啥都没输入，再来一次！")
            continue
        }

        guess = Int64.parse(input)

        if (guess < 1 || guess > 100) {
            println("超出范围！只能在 1 到 100 之间\n")
            continue
        }

        count += 1
        let diff = if (guess > target) { guess - target } else { target - guess }
        if (diff < minDiff) { minDiff = diff }

        if (guess == target) {
            println("\n恭喜！你猜中了！")
            println("正确答案是：${target}，一共猜了 ${count} 次")
        } else {
            let hint = if (guess < target) { "偏小" } else { "偏大" }
            let temp = temperatureHint(diff)
            println("不对！方向：${hint} | 距离提示：${temp}\n")
        }
    }

    println("\nAI 玩家评估：")
    if (count <= 4) { println("传说级 · 二进制先知") }
    else if (count <= 7) { println("大师级 · 二分查找选手？") }
    else if (count <= 12) { println("正常人类") }
    else { println("随机森林（字面意思）") }
}
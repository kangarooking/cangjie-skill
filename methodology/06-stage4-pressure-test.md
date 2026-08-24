# 阶段 4 — 压力测试 (darwin 兼容)

## 目标

在 skill 真正交付之前,用一批测试 prompt 验证它**被调用的精准度**和**被调用后的输出质量**。

不通过的必须回炉 — 不是表面修补 `description` 字段,而是重做阶段 2 的 A2 / E / B。

本阶段新增两项增强机制:

1. **执行质量测试 (`execution_check`)**: 检查 agent 调用 skill 后,是否真的按 E 段执行并忠于作者方法论。
2. **对抗性出题**: 让另一个 agent 只看 name + description,生成容易误触发或漏触发的用户话术,降低自证偏差。

## 为什么必须做

A2 (trigger) 是拆书里最难的环节。一个 skill 做得再漂亮,trigger 不准就等于不存在。压力测试是**唯一**能在发布前发现 trigger 问题的方法。

但只测 trigger 还不够。一个 skill 可能"该调用时确实调用了",却在执行时走偏。例如 E 段要求先识别反例,agent 却直接给建议。这类问题必须用 `execution_check` 测出来。

## 评测原则: 独立 sub-agent 盲测优先

压力测试要尽量模拟真实调用: 一个没有参与蒸馏过程、看不到预期答案的 agent,面对用户 prompt 时是否会自然激活这个 skill,以及激活后是否能按 skill 执行。

优先做法:

- 对每条测试 prompt 启动一个干净的 sub-agent,或在资源有限时对同一个 skill 的一组 prompt 启动一个干净 sub-agent
- 只给 sub-agent: skill 路径或 skill 内容、用户 prompt、可选的相邻 skill 列表
- 不给 sub-agent: `type`、`expected_behavior`、`notes`、通过标准、主流程的判断
- 要求 sub-agent 输出: `would_trigger`、`reason`、`if_triggered_action`
- 对 `execution_check`,还要输出 `execution_trace` 和 `final_answer`
- 主流程再把 sub-agent 输出和 `test-prompts.json` 的预期逐条对比,统计通过率

如果当前环境没有 sub-agent 能力,才退回到主流程自测,并在 `test-results.md` 里标明这是 fallback 结果,可信度低于独立 sub-agent 盲测。

## test-prompts.json 格式 (darwin-skill 兼容)

`execution_check` 是兼容扩展: 保留原有 `test_cases` 数组和 `type` 字段,只新增一种测试类型。不能删除或改名 `should_trigger`、`should_not_trigger`、`edge_case`。

```json
{
  "skill": "inversion-thinking",
  "version": "0.1.0",
  "test_cases": [
    {
      "id": "should-trigger-01",
      "type": "should_trigger",
      "prompt": "我要决定要不要接这个新项目,列了一堆好处但还是没底",
      "expected_behavior": "调用 inversion-thinking, 反问'最不希望发生什么'",
      "notes": "正面场景: 决策纠结"
    },
    {
      "id": "should-not-trigger-01",
      "type": "should_not_trigger",
      "prompt": "帮我查一下这个 API 的参数",
      "expected_behavior": "纯信息查询, 不应调用任何决策 skill",
      "notes": "诱饵: 非决策场景"
    },
    {
      "id": "edge-01",
      "type": "edge_case",
      "prompt": "我在想晚饭吃什么",
      "expected_behavior": "日常琐事, 不应调用 (虽然字面是'决策')",
      "notes": "边界: 区分严肃决策和日常选择"
    },
    {
      "id": "execution-check-01",
      "type": "execution_check",
      "prompt": "我要不要接这个新项目?客户很大,预算也不错,但团队已经很满。",
      "expected_behavior": "应调用 inversion-thinking,并完整执行 E 段: 先列最坏结果,再倒推不可接受风险,最后给出判停建议。",
      "rubric": [
        "是否走完 E 段的关键步骤",
        "是否使用作者方法论的反向推理,而不是泛泛列优缺点",
        "是否给出清晰的判停条件"
      ],
      "notes": "执行质量检查: trigger 正确之外,还要看输出是否忠于方法论"
    }
  ]
}
```

## 四类测试缺一不可

| 类型 | 数量 | 目的 |
|---|---|---|
| `should_trigger` | 3–5 条 | 该调用时是否调用 |
| `should_not_trigger` (诱饵) | 2–3 条 | 不该调用时是否忍住 |
| `edge_case` | 1–3 条 | 边界模糊场景的判断是否合理 |
| `execution_check` | 1–2 条 | 调用后是否按 E 段正确执行 |

**没有诱饵测试的 skill 一律打回**。因为只测 positive case,skill 总会看起来"很好",但实际部署后会乱激活。

**没有 `execution_check` 的 skill 一律打回**。因为 trigger 准确不代表执行正确。

**跨 skill 混淆测试 (硬性要求)**: 诱饵中至少 1 条必须是"应该触发同书另一个 skill"的 prompt。同一本书拆出的 10+ 个 skill 之间互相抢调用,是部署后最常见的真实故障 — 只测"完全无关的场景"发现不了它。盲测时把整包所有 skill 的 name + description 列表给 sub-agent,让它做"该激活哪一个"的选择题,而不只是"要不要激活这一个"的判断题。

## 对抗性出题

在主流程写完基础测试集后,新增一个对抗性出题 agent:

1. 只给它当前 skill 的 `name` 和 `description`。
2. 不给它 R / I / A1 / E / B 正文,也不给预期答案。
3. 要求它生成 3 条用户 prompt:
   - 1 条最容易误触发本 skill 的 prompt
   - 1 条最容易漏触发本 skill 的 prompt
   - 1 条容易和同书相邻 skill 混淆的 prompt
4. 主流程把可用的对抗题并入 `test-prompts.json`,类型按实际情况标为 `should_trigger`、`should_not_trigger` 或 `edge_case`。
5. 如果对抗题暴露 description 太宽或太窄,先修 A2 和 frontmatter `description`,再继续盲测。

## 执行流程

1. 对每个 skill,按模板写 `test-prompts.json`。
2. 运行对抗性出题,把通过人工审查的对抗题并入测试集。
3. 对每个 test_case 做独立盲测: 隐藏 `type` / `expected_behavior` / `notes` / `rubric`,让 sub-agent 判断"是否会调用这个 skill",并在需要时实际执行。
4. 主流程对照 `test-prompts.json` 判卷:
   - `should_trigger`: sub-agent 应明确调用该 skill,且执行动作符合 `expected_behavior`
   - `should_not_trigger`: sub-agent 不应调用该 skill,诱饵测试容错为 0
   - `edge_case`: sub-agent 的判断要符合 `expected_behavior` 中定义的边界理由
   - `execution_check`: sub-agent 应调用该 skill,完整执行 E 段,并满足 `rubric` 中的关键检查点
5. 统计通过率:
   - **100% 通过** → 接受
   - **≥80% 通过** → 分析失败 case, 决定是修 A2 / E / B 还是修测试 (但修测试要警惕自我合理化)
   - **<80% 通过** → **必须回炉重做阶段 2**,不是小修
6. 修复后重新跑,直到通过。

## 判断"修 skill 还是修测试"

- 如果失败的 case 暴露了 skill **trigger 描述有歧义**: 修 A2 和 description。
- 如果 `execution_check` 暴露步骤不清、判停条件缺失、输出容易泛化: 修 E 段。
- 如果失败的 case 是一个你**之前没想到的合理场景**: 可能需要修 A2 / B 以覆盖或明确排除。
- 如果失败的 case 是你**为了凑诱饵而设计过狠的场景**: 修测试 (但必须记录理由)。

## 输出

- `<skill-dir>/test-prompts.json` — darwin 兼容格式
- `<skill-dir>/test-results.md` — 本次测试的通过率、执行质量检查结果和失败分析 (审计用)

## 记分卡指标

本阶段结束时,为阶段 5 的 `SCORECARD.md` 暂存以下数据:

- 每个 skill 的测试用例数
- `should_trigger` / `should_not_trigger` / `edge_case` / `execution_check` 数量
- 首轮通过率
- 最终通过率
- 诱饵失败数
- 执行质量失败数
- 回炉次数
- 是否使用独立 sub-agent 盲测
- 是否使用 fallback 自测

## 下一步

所有 skill 全部通过后,进入阶段 5 (交付),见 `07-stage5-deliver.md`: 生成面向读者的 DIGEST.md 精华长文,生成 SCORECARD.md 质量记分卡,并把 skill 安装到用户的 skills 目录 — 之后才向用户提 darwin-skill 自动进化。
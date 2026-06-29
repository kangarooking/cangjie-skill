# 阶段 4 — 压力测试 (darwin 兼容)

## 目标

在 skill 真正交付之前,用一批测试 prompt 验证它**被调用的精准度**和**被调用后的输出质量**。

不通过的必须回炉 — 不是表面修补 `description` 字段,而是重做阶段 2 的 A2 / E / B。

## 为什么必须做

A2 (trigger) 是拆书里最难的环节。一个 skill 做得再漂亮,trigger 不准就等于不存在。压力测试是**唯一**能在发布前发现 trigger 问题的方法。

## 评测原则: 独立 sub-agent 盲测优先

压力测试要尽量模拟真实调用: 一个没有参与蒸馏过程、看不到预期答案的 agent,面对用户 prompt 时是否会自然激活这个 skill。

优先做法:
- 对每条测试 prompt 启动一个干净的 sub-agent,或在资源有限时对同一个 skill 的一组 prompt 启动一个干净 sub-agent
- 只给 sub-agent: skill 路径或 skill 内容、用户 prompt、可选的相邻 skill 列表
- 不给 sub-agent: `type`、`expected_behavior`、`notes`、通过标准、主流程的判断
- 要求 sub-agent 输出: `would_trigger`、`reason`、`if_triggered_action`
- 主流程再把 sub-agent 输出和 `test-prompts.json` 的预期逐条对比,统计通过率

如果当前环境没有 sub-agent 能力,才退回到主流程自测,并在 `test-results.md` 里标明这是 fallback 结果,可信度低于独立 sub-agent 盲测。

## test-prompts.json 格式 (darwin-skill 兼容)

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
    }
  ]
}
```

## 三类测试缺一不可

| 类型 | 数量 | 目的 |
|---|---|---|
| `should_trigger` | 3–5 条 | 该调用时是否调用 |
| `should_not_trigger` (诱饵) | 2–3 条 | 不该调用时是否忍住 |
| `edge_case` | 1–3 条 | 边界模糊场景的判断是否合理 |

**没有诱饵测试的 skill 一律打回**。因为只测 positive case,skill 总会看起来"很好",但实际部署后会乱激活。

## 执行流程

1. 对每个 skill,按模板写 `test-prompts.json`
2. 对每个 test_case 做独立盲测: 隐藏 `type` / `expected_behavior` / `notes`,让 sub-agent 判断"是否会调用这个 skill",记录判断和理由
3. 主流程对照 `test-prompts.json` 判卷:
   - `should_trigger`: sub-agent 应明确调用该 skill,且执行动作符合 `expected_behavior`
   - `should_not_trigger`: sub-agent 不应调用该 skill,诱饵测试容错为 0
   - `edge_case`: sub-agent 的判断要符合 `expected_behavior` 中定义的边界理由
4. 统计通过率:
   - **100% 通过** → 接受
   - **≥80% 通过** → 分析失败 case, 决定是修 A2 还是修测试 (但修测试要警惕自我合理化)
   - **<80% 通过** → **必须回炉重做阶段 2**,不是小修
5. 修复后重新跑,直到通过

## 判断"修 skill 还是修测试"

- 如果失败的 case 暴露了 skill **trigger 描述有歧义**: 修 skill
- 如果失败的 case 是一个你**之前没想到的合理场景**: 可能需要修 skill 以覆盖或明确排除
- 如果失败的 case 是你**为了凑诱饵而设计过狠的场景**: 修测试 (但必须记录理由)

## 输出

- `<skill-dir>/test-prompts.json` — darwin 兼容格式
- `<skill-dir>/test-results.md` — 本次测试的通过率和失败分析 (审计用)

## 与 darwin-skill 的交接

所有 skill 全部通过后,告诉用户:
> 已完成。如需持续进化,可以喂给 darwin-skill:
> `darwin evolve books/<slug>/`
> 它会用这里的 test-prompts.json 做 ratcheting 自动进化。

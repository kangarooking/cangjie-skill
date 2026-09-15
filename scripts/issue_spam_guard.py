#!/usr/bin/env python3
"""issue_spam_guard.py — issue 广告/垃圾内容自动识别与清理。

由 .github/workflows/issue-guard.yml 在 issue opened/edited 时调用：
- 规则打分（广告关键词 + 域名信誉 + 外链/图片特征），规则见 .github/issue-guard-rules.json
- 高分（>= close_score）：打 suspected-spam 标签、留提示评论、自动关闭
- 中分（>= flag_score）：仅打标签 + 评论，交维护者复核
- 维护者 reopen 后自动移除标签，不再重复处理

只做启发式识别，宁可漏判不误判；所有处置均留痕、可恢复（issue 可随时 reopen）。
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

RULES_PATH = Path(__file__).parent.parent / ".github" / "issue-guard-rules.json"
API = "https://api.github.com"

# 高置信组合：推广用语 + 外链同时出现才算重罪，避免误伤正常求助
PROMO_PHRASES = [
    "官网链接", "注册领取", "免费领取", "限时优惠", "邀请码", "优惠码",
    "扫码关注", "加微信", "加QQ", "私聊我", "代理注册", "测速图",
    "还是真的稳", "别等下一波", "跑路", "机场", "翻墙", "梯子", "专线",
]


def api(method: str, path: str, token: str, payload: dict | None = None) -> dict:
    req = Request(
        f"{API}{path}",
        data=json.dumps(payload).encode() if payload else None,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "issue-spam-guard",
        },
    )
    with urlopen(req) as resp:
        return json.loads(resp.read() or b"{}")


def score_issue(title: str, body: str, rules: dict) -> tuple[int, list[str]]:
    """返回 (总分, 命中的规则说明)。只统计正文，评论不参与（避免误伤讨论串）。"""
    text = f"{title}\n{body}"
    hits: list[str] = []
    score = 0

    for kw in rules.get("ad_keywords", []):
        if kw.lower() in text.lower():
            score += int(rules.get("keyword_weight", 2))
            hits.append(f"关键词「{kw}」")

    for pat in rules.get("url_patterns", []):
        if re.search(pat, text, re.IGNORECASE):
            score += int(rules.get("url_weight", 4))
            hits.append(f"可疑推广链接模式 /{pat}/")

    promo = [p for p in PROMO_PHRASES if p in text]
    if len(promo) >= int(rules.get("promo_phrase_threshold", 2)):
        score += int(rules.get("promo_phrase_weight", 4))
        hits.append(f"推广话术组合：{'、'.join(promo[:5])}")

    # 外部图片直链（正常 issue 很少贴 user-images 之外的图床）
    for img in re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)", text):
        if not re.search(rules.get("trusted_image_hosts", "user-images\\.githubusercontent\\.com"), img):
            score += int(rules.get("foreign_image_weight", 3))
            hits.append(f"非受信图床直链：{img[:60]}")

    return score, hits


def main() -> int:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    action = event.get("action", "")
    issue = event["issue"]
    number = issue["number"]

    # 维护者主动 reopen = 人工改判，移除标签后退出
    if action == "reopened":
        api("DELETE", f"/repos/{repo}/issues/{number}/labels/suspected-spam", token)
        print(f"#{number} 被人工 reopen，已移除 suspected-spam 标签")
        return 0

    if action not in ("opened", "edited"):
        return 0
    if "suspected-spam" in {l["name"] for l in issue.get("labels", [])}:
        return 0  # 已标记过，避免编辑后重复评论

    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    score, hits = score_issue(issue["title"], issue.get("body") or "", rules)
    print(f"#{number} spam score = {score}；命中：{hits or '无'}")

    close_score = int(rules.get("close_score", 10))
    flag_score = int(rules.get("flag_score", 6))
    if score < flag_score:
        return 0

    evidence = "\n".join(f"- {h}" for h in hits)
    label = api("POST", f"/repos/{repo}/issues/{number}/labels", token,
                {"labels": ["suspected-spam"]})
    comment = (
        f"🤖 **issue-guard 自动检测**：本 issue 疑似广告/垃圾内容（评分 {score}）。\n\n"
        f"命中规则：\n{evidence}\n\n"
        "已自动关闭。如为误判，请维护者 reopen，机器人会自动移除标记并保留内容。"
    )
    api("POST", f"/repos/{repo}/issues/{number}/comments", token, {"body": comment})
    if score >= close_score:
        api("PATCH", f"/repos/{repo}/issues/{number}", token,
            {"state": "closed", "state_reason": "not_planned"})
        print(f"#{number} 已自动关闭")
    else:
        print(f"#{number} 已打标待人工复核")
    return 0


if __name__ == "__main__":
    sys.exit(main())

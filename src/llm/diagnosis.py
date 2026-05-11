from __future__ import annotations

from typing import Any

import requests


def _fallback_summary(result: dict[str, Any]) -> str:
    dim = result.get("dimension_scores", {})
    sorted_dim = sorted(dim.items(), key=lambda x: x[1], reverse=True)
    top = "、".join([f"{k}({v})" for k, v in sorted_dim[:2]]) if sorted_dim else "暂无"
    low = "、".join([f"{k}({v})" for k, v in sorted_dim[-2:]]) if sorted_dim else "暂无"
    total = result.get("total_score", 0)
    return (
        f"该品牌综合得分为 {total} 分，整体处于中高水平。优势维度主要体现在 {top}，"
        f"说明品牌在核心经营与消费端口碑方面具备一定竞争力。相对薄弱的维度为 {low}，"
        "建议后续优先补强相关数据监测并进行针对性优化。当前结论基于样例数据计算，"
        "仍需结合更长期销量与供应链履约数据持续校准。"
    )


def generate_diagnosis(
    score_result: dict[str, Any],
    model: str,
    api_key: str,
    base_url: str,
) -> str:
    if not api_key:
        return _fallback_summary(score_result)

    prompt = (
        "你是零售品牌分析顾问。请基于以下评分结果，输出100-200字中文综合诊断。"
        "要求：1) 先给总体判断；2) 点出优势维度和短板维度；3) 给1-2条可执行建议；"
        "4) 禁止编造未给出的数据。\\n\\n"
        f"评分结果：{score_result}"
    )

    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨、简洁的品牌数据分析专家。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 220,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        return content[:400]
    except Exception:
        return _fallback_summary(score_result)

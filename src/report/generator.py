from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def _plot_radar(dimension_scores: dict[str, float], output_path: Path) -> None:
    label_map = {
        "品牌成熟度": "Maturity",
        "产品质量": "Quality",
        "市场需求匹配度": "Demand Fit",
        "创新力": "Innovation",
        "供应链可靠性": "Supply Chain",
        "性价比": "Value",
    }
    labels = [label_map.get(k, k) for k in dimension_scores.keys()]
    values = list(dimension_scores.values())
    if not labels:
        return

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    ax.set_title("Brand Multi-Dimension Radar")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def generate_markdown_report(
    score_result: dict[str, Any],
    diagnosis_text: str,
    output_dir: Path,
    save_chart: bool = True,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "brand_report.md"
    chart_path = output_dir / "score_radar.png"

    if save_chart:
        _plot_radar(score_result["dimension_scores"], chart_path)

    lines = [
        "# 品牌多维度评分报告",
        "",
        f"- 综合得分：**{score_result['total_score']}**",
        "",
        "## 各维度得分",
        "",
        "| 维度 | 得分 | 置信度 |",
        "|---|---:|---|",
    ]

    for dim, score in score_result["dimension_scores"].items():
        conf = score_result["dimension_confidence"].get(dim, "medium")
        lines.append(f"| {dim} | {score} | {conf} |")

    lines.extend(
        [
            "",
            "## 评分说明",
            "",
            "- 各维度得分范围 0-100，分值越高表示该维度表现越强。",
            "- 低置信度维度在综合评分中按系数降权处理。",
            "- 具体公式见 `docs/METRIC_DESIGN.md`。",
            "",
            "## LLM 综合诊断（deepseek-v4-flash）",
            "",
            diagnosis_text,
        ]
    )

    if save_chart:
        lines.extend(["", "## 可视化图表", "", "![雷达图](score_radar.png)"])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path

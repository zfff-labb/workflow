from __future__ import annotations

from typing import Any

import numpy as np


def _clip_0_100(value: float) -> float:
    return float(max(0.0, min(100.0, value)))


def _linear_score(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return _clip_0_100((value - low) / (high - low) * 100.0)


def _inverse_linear_score(value: float, low: float, high: float) -> float:
    return _clip_0_100(100.0 - _linear_score(value, low, high))


def _weighted(items: list[tuple[float, float]]) -> float:
    total_w = sum(w for _, w in items)
    if total_w <= 0:
        return 0.0
    return float(sum(v * w for v, w in items) / total_w)


def compute_scores(extracted: dict[str, Any]) -> dict[str, Any]:
    m = extracted["metrics"]

    bm = m["brand_maturity"]
    bm_score = _weighted(
        [
            (_linear_score(bm["years_on_market"], 0, 8), 0.35),
            (_linear_score(np.log1p(bm["estimated_visits"]), 0, np.log1p(2_000_000)), 0.40),
            (_inverse_linear_score(bm["visits_cv_3m"], 0, 0.8), 0.25),
        ]
    )

    pq = m["product_quality"]
    pq_score = _weighted(
        [
            (_linear_score(pq["avg_stars"], 1, 5), 0.50),
            (_inverse_linear_score(pq["low_star_ratio"], 0, 0.5), 0.25),
            (_inverse_linear_score(pq["quality_negative_ratio"], 0, 0.4), 0.25),
        ]
    )

    md = m["market_demand_fit"]
    md_score = _weighted(
        [
            (_linear_score(np.log1p(md["visits_mean_3m"]), 0, np.log1p(800_000)), 0.45),
            (_linear_score(md["high_star_ratio"], 0, 1), 0.35),
            (_linear_score(md["repeat_purchase_ratio"], 0, 0.5), 0.20),
        ]
    )

    iv = m["innovation"]
    new_ratio = (iv["new_products_last_365d"] / iv["valid_product_count"]) if iv["valid_product_count"] > 0 else 0.0
    iv_score = _weighted(
        [
            (_linear_score(new_ratio, 0, 0.5), 0.40),
            (_linear_score(iv["recent_activity_365d"], 0, 25), 0.40),
            (_inverse_linear_score(iv["product_line_freshness_days"], 60, 1200), 0.20),
        ]
    )

    sc = m["supply_chain_reliability"]
    sc_score = _weighted(
        [
            (_linear_score(sc["available_variant_ratio"], 0, 1), 0.45),
            (_inverse_linear_score(sc["supply_issue_ratio"], 0, 0.2), 0.35),
            (_linear_score(sc["shipping_carrier_count"], 1, 3), 0.20),
        ]
    )

    vf = m["value_for_money"]
    value_sentiment = (vf["value_positive_ratio"] - vf["value_negative_ratio"] + 1) / 2
    vf_score = _weighted(
        [
            (_inverse_linear_score(vf["avg_variant_price"], 2, 40), 0.25),
            (_linear_score(value_sentiment, 0, 1), 0.45),
            (_linear_score(vf["avg_stars"], 1, 5), 0.30),
        ]
    )

    dimensions = {
        "品牌成熟度": round(bm_score, 2),
        "产品质量": round(pq_score, 2),
        "市场需求匹配度": round(md_score, 2),
        "创新力": round(iv_score, 2),
        "供应链可靠性": round(sc_score, 2),
        "性价比": round(vf_score, 2),
    }

    confidences = {
        "品牌成熟度": "high",
        "产品质量": "medium" if pq.get("review_count", 0) < 100 else "high",
        "市场需求匹配度": "medium",
        "创新力": "medium",
        "供应链可靠性": "low" if sc.get("supply_issue_ratio", 0) < 0.02 else "medium",
        "性价比": "medium",
    }

    # low confidence dimensions participate with lower weight.
    base_weights = {
        "品牌成熟度": 0.22,
        "产品质量": 0.20,
        "市场需求匹配度": 0.18,
        "创新力": 0.14,
        "供应链可靠性": 0.12,
        "性价比": 0.14,
    }
    confidence_factor = {"high": 1.0, "medium": 0.85, "low": 0.60}

    weighted_values = []
    for k, v in dimensions.items():
        w = base_weights[k] * confidence_factor[confidences[k]]
        weighted_values.append((v, w))
    total_score = round(_weighted(weighted_values), 2)

    return {
        "dimension_scores": dimensions,
        "dimension_confidence": confidences,
        "total_score": total_score,
    }

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from src.data.loader import LoadedData


def _safe_mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def _contains_any(text: str, keywords: list[str]) -> bool:
    t = text.lower()
    return any(k in t for k in keywords)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def extract_metrics(data: LoadedData) -> dict[str, Any]:
    domain = data.brand_info.get("domain", {})
    traffic = data.traffic_info
    reviews = data.review_info
    products = data.products_info.get("products", [])
    cards = data.company_info.get("cards", {})

    now = datetime.now(timezone.utc)
    created_at = _parse_dt(domain.get("created_at"))
    years_on_market = (
        max(0.0, (now - created_at.astimezone(timezone.utc)).days / 365.25)
        if created_at
        else 0.0
    )

    monthly_visits_map = traffic.get("EstimatedMonthlyVisits", {})
    monthly_visits = [float(v) for v in monthly_visits_map.values()] if monthly_visits_map else []
    visits_mean_3m = _safe_mean(monthly_visits)
    visits_cv_3m = float(np.std(monthly_visits) / np.mean(monthly_visits)) if monthly_visits and np.mean(monthly_visits) > 0 else 0.0

    review_df = pd.DataFrame(reviews)
    if review_df.empty:
        review_df = pd.DataFrame(columns=["stars", "bodyPositive", "bodyNegative"])
    review_df["stars"] = pd.to_numeric(review_df.get("stars"), errors="coerce")
    review_df["text"] = review_df.get("bodyPositive", "").fillna("").astype(str) + " " + review_df.get("bodyNegative", "").fillna("").astype(str)

    avg_stars = float(review_df["stars"].mean()) if not review_df["stars"].dropna().empty else 0.0
    low_star_ratio = float((review_df["stars"] <= 2).mean()) if not review_df.empty else 0.0
    high_star_ratio = float((review_df["stars"] >= 4).mean()) if not review_df.empty else 0.0

    quality_neg_kw = ["artificial", "aftertaste", "too sweet", "didn't taste good", "not good", "missed the mark"]
    supply_kw = ["shipping", "delay", "late", "out of stock", "delivery"]
    repeat_kw = ["always", "regular", "keep", "go-to", "hooked", "staple"]
    value_pos_kw = ["worth", "sale", "deal", "good alternative", "better-for-you"]
    value_neg_kw = ["expensive", "pricey", "cost a lot", "too expensive", "price is high"]

    quality_neg_ratio = float(review_df["text"].apply(lambda t: _contains_any(t, quality_neg_kw)).mean()) if not review_df.empty else 0.0
    supply_issue_ratio = float(review_df["text"].apply(lambda t: _contains_any(t, supply_kw)).mean()) if not review_df.empty else 0.0
    repeat_purchase_ratio = float(review_df["text"].apply(lambda t: _contains_any(t, repeat_kw)).mean()) if not review_df.empty else 0.0
    value_pos_ratio = float(review_df["text"].apply(lambda t: _contains_any(t, value_pos_kw)).mean()) if not review_df.empty else 0.0
    value_neg_ratio = float(review_df["text"].apply(lambda t: _contains_any(t, value_neg_kw)).mean()) if not review_df.empty else 0.0

    valid_products: list[dict[str, Any]] = []
    for p in products:
        vendor = str(p.get("vendor", "")).lower()
        tags = [str(t).lower() for t in p.get("tags", [])]
        if vendor != "olipop":
            continue
        if any("test" in t or "dev_" in t or "dev" == t for t in tags):
            continue
        valid_products.append(p)

    product_created_dates: list[datetime] = []
    all_variant_prices: list[float] = []
    variant_available_flags: list[bool] = []
    for p in valid_products:
        dt = _parse_dt(p.get("created_at"))
        if dt:
            product_created_dates.append(dt.astimezone(timezone.utc))
        for v in p.get("variants", []):
            try:
                all_variant_prices.append(float(v.get("price")))
            except (TypeError, ValueError):
                pass
            variant_available_flags.append(bool(v.get("available")))

    latest_product_dt = max(product_created_dates) if product_created_dates else None
    new_products_last_365d = 0
    if latest_product_dt:
        new_products_last_365d = sum(1 for dt in product_created_dates if (latest_product_dt - dt).days <= 365)

    product_line_freshness_days = (
        float(np.median([(now - dt).days for dt in product_created_dates])) if product_created_dates else 9999.0
    )

    timeline_entities = cards.get("overview_timeline", {}).get("entities", [])
    recent_activity_365d = 0
    for item in timeline_entities:
        p = item.get("properties", {})
        act_date = _parse_dt(p.get("activity_date"))
        if not act_date:
            continue
        if (now - act_date.astimezone(timezone.utc)).days <= 365:
            recent_activity_365d += 1

    metrics = {
        "brand_maturity": {
            "years_on_market": years_on_market,
            "estimated_visits": float(domain.get("estimated_visits", 0) or 0),
            "visits_mean_3m": visits_mean_3m,
            "visits_cv_3m": visits_cv_3m,
        },
        "product_quality": {
            "avg_stars": avg_stars,
            "low_star_ratio": low_star_ratio,
            "quality_negative_ratio": quality_neg_ratio,
            "review_count": int(len(review_df)),
        },
        "market_demand_fit": {
            "visits_mean_3m": visits_mean_3m,
            "high_star_ratio": high_star_ratio,
            "repeat_purchase_ratio": repeat_purchase_ratio,
        },
        "innovation": {
            "valid_product_count": int(len(valid_products)),
            "new_products_last_365d": int(new_products_last_365d),
            "recent_activity_365d": int(recent_activity_365d),
            "product_line_freshness_days": product_line_freshness_days,
        },
        "supply_chain_reliability": {
            "available_variant_ratio": float(np.mean(variant_available_flags)) if variant_available_flags else 0.0,
            "supply_issue_ratio": supply_issue_ratio,
            "shipping_carrier_count": int(len(domain.get("shipping_carriers", []))),
        },
        "value_for_money": {
            "avg_variant_price": _safe_mean(all_variant_prices),
            "value_positive_ratio": value_pos_ratio,
            "value_negative_ratio": value_neg_ratio,
            "avg_stars": avg_stars,
        },
    }

    return {"metrics": metrics}

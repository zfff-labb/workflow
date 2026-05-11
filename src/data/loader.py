from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LoadedData:
    brand_info: dict[str, Any]
    company_info: dict[str, Any]
    products_info: dict[str, Any]
    traffic_info: dict[str, Any]
    review_info: list[dict[str, Any]]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_all_data(data_dir: Path) -> LoadedData:
    return LoadedData(
        brand_info=_load_json(data_dir / "brand-info.json"),
        company_info=_load_json(data_dir / "company-info.json"),
        products_info=_load_json(data_dir / "products-info.json"),
        traffic_info=_load_json(data_dir / "traffic-info.json"),
        review_info=_load_json(data_dir / "review-info.json"),
    )

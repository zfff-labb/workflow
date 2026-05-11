from __future__ import annotations

import json
from pathlib import Path

from src.config.settings import get_settings
from src.data.loader import load_all_data
from src.features.metric_extractor import extract_metrics
from src.llm.diagnosis import generate_diagnosis
from src.report.generator import generate_markdown_report
from src.scoring.scorer import compute_scores


def run_workflow() -> dict:
    settings = get_settings()
    data = load_all_data(settings.data_dir)
    extracted = extract_metrics(data)
    score_result = compute_scores(extracted)

    diagnosis_text = generate_diagnosis(
        score_result=score_result,
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )
    report_path = generate_markdown_report(
        score_result=score_result,
        diagnosis_text=diagnosis_text,
        output_dir=settings.output_dir,
        save_chart=True,
    )

    metrics_dump = settings.output_dir / "metrics_and_scores.json"
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    metrics_dump.write_text(
        json.dumps(
            {
                "metrics": extracted["metrics"],
                "score_result": score_result,
                "diagnosis": diagnosis_text,
                "report_path": str(report_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"report_path": str(report_path), "metrics_path": str(metrics_dump)}


if __name__ == "__main__":
    result = run_workflow()
    print(json.dumps(result, ensure_ascii=False, indent=2))

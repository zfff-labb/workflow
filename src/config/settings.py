from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data_dir: Path
    output_dir: Path
    deepseek_api_key: str
    deepseek_model: str
    deepseek_base_url: str


def get_settings() -> Settings:
    root = Path(__file__).resolve().parents[2]
    return Settings(
        project_root=root,
        data_dir=root / "sample-data",
        output_dir=root / "outputs",
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )

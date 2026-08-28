from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


@dataclass
class LLMConfig:
    provider: str = "mock"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7


@dataclass
class GenerationConfig:
    num_suggestions: int = 3
    max_context_messages: int = 30
    style: str = "自然、口语化，像真实微信聊天"
    language: str = "zh"


@dataclass
class AppConfig:
    user_name: str = "我"
    llm: LLMConfig = field(default_factory=LLMConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    log_level: str = "INFO"


def _resolve_env(value: str) -> str:
    if value.startswith("${") and value.endswith("}"):
        return os.environ.get(value[2:-1], "")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def load_app_config(path: Path | None = None) -> AppConfig:
    config_path = path or CONFIG_DIR / "config.yaml"
    if not config_path.exists():
        config_path = CONFIG_DIR / "config.example.yaml"
        logger.warning("未找到 config.yaml，使用 config.example.yaml")

    data = _load_yaml(config_path)
    llm_data = data.get("llm", {})
    gen_data = data.get("generation", {})

    return AppConfig(
        user_name=data.get("user_name", "我"),
        llm=LLMConfig(
            provider=llm_data.get("provider", "mock"),
            api_key=_resolve_env(llm_data.get("api_key", "")),
            base_url=llm_data.get("base_url", "https://api.openai.com/v1"),
            model=llm_data.get("model", "gpt-4o-mini"),
            temperature=float(llm_data.get("temperature", 0.7)),
        ),
        generation=GenerationConfig(
            num_suggestions=int(gen_data.get("num_suggestions", 3)),
            max_context_messages=int(gen_data.get("max_context_messages", 30)),
            style=gen_data.get("style", "自然、口语化，像真实微信聊天"),
            language=gen_data.get("language", "zh"),
        ),
        log_level=data.get("log_level", "INFO"),
    )

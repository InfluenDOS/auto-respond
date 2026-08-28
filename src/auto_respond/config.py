from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


@dataclass
class AppConfig:
    adapter: str = "mock"
    whitelist: list[str] = field(default_factory=list)
    blacklist: list[str] = field(default_factory=list)
    default_cooldown: int = 60
    log_level: str = "INFO"


@dataclass
class Rule:
    name: str
    enabled: bool
    match_type: str
    pattern: str
    reply: str
    senders: list[str] = field(default_factory=list)
    cooldown: int | None = None


@dataclass
class RulesConfig:
    rules: list[Rule] = field(default_factory=list)


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
    return AppConfig(
        adapter=data.get("adapter", "mock"),
        whitelist=data.get("whitelist") or [],
        blacklist=data.get("blacklist") or [],
        default_cooldown=int(data.get("default_cooldown", 60)),
        log_level=data.get("log_level", "INFO"),
    )


def load_rules(path: Path | None = None) -> RulesConfig:
    rules_path = path or CONFIG_DIR / "rules.yaml"
    if not rules_path.exists():
        rules_path = CONFIG_DIR / "rules.example.yaml"
        logger.warning("未找到 rules.yaml，使用 rules.example.yaml")

    data = _load_yaml(rules_path)
    rules = []
    for item in data.get("rules", []):
        rules.append(
            Rule(
                name=item["name"],
                enabled=item.get("enabled", True),
                match_type=item.get("match_type", "contains"),
                pattern=item["pattern"],
                reply=item["reply"],
                senders=item.get("senders") or [],
                cooldown=item.get("cooldown"),
            )
        )
    return RulesConfig(rules=rules)

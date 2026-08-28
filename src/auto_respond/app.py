from __future__ import annotations

import argparse
import logging
import signal
import sys
from pathlib import Path

from auto_respond.adapters import create_adapter
from auto_respond.config import load_app_config, load_rules
from auto_respond.handlers import MessageHandler
from auto_respond.rules import RulesEngine


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="微信消息自动回复")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="使用 Mock 模式测试规则（无需微信）",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="配置文件路径",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=None,
        help="规则文件路径",
    )
    args = parser.parse_args()

    app_config = load_app_config(args.config)
    if args.mock:
        app_config.adapter = "mock"

    _setup_logging(app_config.log_level)
    logger = logging.getLogger("auto_respond")

    rules_config = load_rules(args.rules)
    engine = RulesEngine(app_config, rules_config)
    adapter = create_adapter(app_config.adapter)
    handler = MessageHandler(engine, adapter)

    enabled_rules = [r.name for r in rules_config.rules if r.enabled]
    logger.info("已加载 %d 条启用规则: %s", len(enabled_rules), ", ".join(enabled_rules))
    logger.info("适配器: %s", app_config.adapter)

    def on_message(message):
        handler.handle(message)

    def _shutdown(signum, frame):
        logger.info("正在退出...")
        adapter.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        adapter.start(on_message)
    finally:
        adapter.stop()


if __name__ == "__main__":
    main()

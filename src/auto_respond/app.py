from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from auto_respond.chat.loader import load_conversation, load_from_paste
from auto_respond.config import load_app_config
from auto_respond.generator import create_generator
from auto_respond.models import Conversation


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_conversation(conversation: Conversation) -> None:
    print(f"\n--- 与「{conversation.contact or '对方'}」的聊天记录 ---")
    for msg in conversation.messages:
        prefix = "我" if msg.is_self else msg.sender
        print(f"  {prefix}: {msg.content}")
    print()


def _print_suggestions(suggestions: list[str]) -> None:
    print("--- 回复建议 ---")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n  [{i}] {suggestion}")
    print("\n提示：复制你喜欢的回复，手动发送到微信。")
    print()


def cmd_suggest(args: argparse.Namespace) -> None:
    config = load_app_config(args.config)
    if args.mock:
        config.llm.provider = "mock"

    _setup_logging(config.log_level)
    logger = logging.getLogger("auto_respond")

    if args.paste:
        conversation = load_from_paste(user_name=config.user_name)
    elif args.chat:
        conversation = load_conversation(args.chat, user_name=config.user_name)
    else:
        print("请指定 --chat 文件路径，或使用 --paste 粘贴聊天记录", file=sys.stderr)
        sys.exit(1)

    if not conversation.messages:
        print("未解析到任何消息，请检查聊天记录格式。", file=sys.stderr)
        sys.exit(1)

    _print_conversation(conversation)

    if not conversation.needs_reply():
        print("最后一条消息是你自己发的，可能不需要回复。")
        if not args.force:
            answer = input("仍要生成建议？(y/N) ").strip().lower()
            if answer != "y":
                return

    generator = create_generator(config)
    logger.info("使用 %s 生成回复建议...", config.llm.provider)

    suggestions = generator.generate(conversation, config)
    if not suggestions:
        print("未能生成回复建议，请检查配置或重试。", file=sys.stderr)
        sys.exit(1)

    _print_suggestions(suggestions)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="根据微信聊天记录，智能生成回复建议（不自动发送）"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    suggest_parser = subparsers.add_parser("suggest", help="根据聊天记录生成回复建议")
    suggest_parser.add_argument(
        "--chat", "-c",
        type=Path,
        help="聊天记录文件（.txt 或 .json）",
    )
    suggest_parser.add_argument(
        "--paste", "-p",
        action="store_true",
        help="交互式粘贴聊天记录",
    )
    suggest_parser.add_argument(
        "--mock",
        action="store_true",
        help="使用 Mock 模式（无需 API Key）",
    )
    suggest_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="即使最后一条是自己发的也生成建议",
    )
    suggest_parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="配置文件路径",
    )
    suggest_parser.set_defaults(func=cmd_suggest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

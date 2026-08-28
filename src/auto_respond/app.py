from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from auto_respond.config import load_app_config
from auto_respond.service import SuggestService


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_conversation(conversation) -> None:
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


def cmd_list(args: argparse.Namespace) -> None:
    config = load_app_config(args.config)
    service = SuggestService(config)
    chats = service.list_chats()
    if not chats:
        print("未配置任何聊天记录，请编辑 config/chats.yaml")
        return
    print("已指定的聊天记录：")
    for chat in chats:
        print(f"  {chat.id:12} {chat.name:8} {chat.file}")


def cmd_suggest(args: argparse.Namespace) -> None:
    config = load_app_config(args.config)
    if args.mock:
        config.llm.provider = "mock"

    _setup_logging(config.log_level)
    service = SuggestService(config)

    if not args.id:
        print("请使用 --id 指定聊天记录（先用 list 命令查看）", file=sys.stderr)
        sys.exit(1)

    try:
        conversation, suggestions = service.suggest(args.id, force=args.force)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    _print_conversation(conversation)
    _print_suggestions(suggestions)


def cmd_gui(args: argparse.Namespace) -> None:
    from auto_respond.gui import run_gui

    config = load_app_config(args.config)
    if args.mock:
        config.llm.provider = "mock"
    run_gui(config)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="根据微信聊天记录，智能生成回复建议（不自动发送）"
    )
    parser.add_argument("--config", type=Path, default=None, help="配置文件路径")
    parser.add_argument("--mock", action="store_true", help="使用 Mock 模式（无需 API Key）")

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="列出已指定的聊天记录")
    list_parser.set_defaults(func=cmd_list)

    suggest_parser = subparsers.add_parser("suggest", help="为指定聊天生成回复建议")
    suggest_parser.add_argument("--id", "-i", required=True, help="聊天记录 ID（在 chats.yaml 中配置）")
    suggest_parser.add_argument("--force", "-f", action="store_true", help="强制生成建议")
    suggest_parser.add_argument("--mock", action="store_true", help="使用 Mock 模式（无需 API Key）")
    suggest_parser.set_defaults(func=cmd_suggest)

    gui_parser = subparsers.add_parser("gui", help="打开桌面图形界面")
    gui_parser.add_argument("--mock", action="store_true", help="使用 Mock 模式（无需 API Key）")
    gui_parser.set_defaults(func=cmd_gui)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

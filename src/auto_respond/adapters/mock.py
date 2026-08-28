from __future__ import annotations

import logging
import sys
import threading
import time
from collections.abc import Callable

from auto_respond.adapters.base import WeChatAdapter
from auto_respond.rules import IncomingMessage

logger = logging.getLogger(__name__)


class MockAdapter(WeChatAdapter):
    """Mock 适配器，用于本地测试规则，无需连接微信。"""

    def __init__(self) -> None:
        self._running = False
        self._on_message: Callable[[IncomingMessage], None] | None = None

    def start(self, on_message: Callable[[IncomingMessage], None]) -> None:
        self._on_message = on_message
        self._running = True
        logger.info("Mock 模式已启动。输入消息测试自动回复，输入 quit 退出。")
        print("\n=== Mock 模式 ===")
        print("格式: [发送者名] 消息内容")
        print("示例: 张三 你好")
        print("输入 quit 退出\n")

        while self._running:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not line:
                continue
            if line.lower() == "quit":
                break

            if " " in line:
                sender, content = line.split(" ", 1)
            else:
                sender, content = "测试用户", line

            message = IncomingMessage(
                sender_id=f"mock_{sender}",
                sender_name=sender,
                content=content,
            )
            if self._on_message:
                self._on_message(message)

        self._running = False

    def send_text(self, target: str, content: str, is_group: bool = False) -> bool:
        prefix = f"[群:{target}]" if is_group else f"[{target}]"
        print(f"\n{prefix} 自动回复: {content}\n")
        return True

    def stop(self) -> None:
        self._running = False

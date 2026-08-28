from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from auto_respond.rules import IncomingMessage


class WeChatAdapter(ABC):
    @abstractmethod
    def start(self, on_message: Callable[[IncomingMessage], None]) -> None:
        """启动监听，收到消息时调用 on_message 回调。"""

    @abstractmethod
    def send_text(self, target: str, content: str, is_group: bool = False) -> bool:
        """发送文本消息。"""

    @abstractmethod
    def stop(self) -> None:
        """停止监听并释放资源。"""

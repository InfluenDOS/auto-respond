from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatMessage:
    sender: str
    content: str
    timestamp: datetime | None = None
    is_self: bool = False


@dataclass
class Conversation:
    contact: str = ""
    messages: list[ChatMessage] = field(default_factory=list)

    @property
    def last_message(self) -> ChatMessage | None:
        return self.messages[-1] if self.messages else None

    def needs_reply(self) -> bool:
        """最后一条消息是否来自对方（需要我回复）。"""
        last = self.last_message
        return last is not None and not last.is_self

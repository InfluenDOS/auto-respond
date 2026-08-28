from __future__ import annotations

from abc import ABC, abstractmethod

from auto_respond.config import AppConfig
from auto_respond.models import Conversation


class ReplyGenerator(ABC):
    @abstractmethod
    def generate(self, conversation: Conversation, config: AppConfig) -> list[str]:
        """根据聊天记录生成回复建议。"""

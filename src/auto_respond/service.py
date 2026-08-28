from __future__ import annotations

import logging

from auto_respond.chat.registry import ChatRegistry, load_chat_registry
from auto_respond.config import AppConfig
from auto_respond.generator import create_generator
from auto_respond.models import Conversation
from auto_respond.style import StyleProfile, learn_style

logger = logging.getLogger(__name__)


class SuggestService:
    def __init__(self, config: AppConfig, registry: ChatRegistry | None = None) -> None:
        self.config = config
        self.registry = registry or load_chat_registry()

    def list_chats(self) -> list:
        return self.registry.list_enabled()

    def load_chat(self, chat_id: str) -> Conversation:
        return self.registry.load(chat_id, user_name=self.config.user_name)

    def build_style_profile(self) -> StyleProfile | None:
        conversations = self.registry.load_all_enabled(user_name=self.config.user_name)
        return learn_style(conversations, self.config)

    def suggest(
        self,
        chat_id: str,
        *,
        force: bool = False,
        style_profile: StyleProfile | None = None,
    ) -> tuple[Conversation, list[str]]:
        conversation = self.load_chat(chat_id)

        if not conversation.messages:
            raise ValueError("聊天记录为空")

        if not conversation.needs_reply() and not force:
            raise ValueError("最后一条消息是你自己发的，可能不需要回复")

        if style_profile is None:
            style_profile = self.build_style_profile()

        generator = create_generator(self.config)
        logger.info("为 [%s] 生成回复建议，风格样本 %d 条", chat_id, len(style_profile.samples) if style_profile else 0)
        suggestions = generator.generate(conversation, self.config, style_profile=style_profile)
        return conversation, suggestions

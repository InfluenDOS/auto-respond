from __future__ import annotations

import logging

from auto_respond.adapters.base import WeChatAdapter
from auto_respond.rules import IncomingMessage, RulesEngine

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, engine: RulesEngine, adapter: WeChatAdapter) -> None:
        self.engine = engine
        self.adapter = adapter

    def handle(self, message: IncomingMessage) -> None:
        logger.debug(
            "收到消息 from=%s content=%r group=%s",
            message.sender_name,
            message.content,
            message.is_group,
        )

        result = self.engine.match(message)
        if not result:
            return

        target = message.room_id if message.is_group else message.sender_id
        logger.info(
            "规则 [%s] 匹配，回复 %s: %s",
            result.rule.name,
            message.sender_name,
            result.reply,
        )
        self.adapter.send_text(target, result.reply, is_group=message.is_group)

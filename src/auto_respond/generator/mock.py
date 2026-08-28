from __future__ import annotations

from auto_respond.config import AppConfig
from auto_respond.generator.base import ReplyGenerator
from auto_respond.models import Conversation


class MockGenerator(ReplyGenerator):
    """无需 API Key 的本地模拟生成器，用于测试流程。"""

    def generate(self, conversation: Conversation, config: AppConfig) -> list[str]:
        last = conversation.last_message
        content = last.content if last else ""
        contact = conversation.contact or "对方"

        suggestions = [
            f"好的，没问题！",
            f"收到，我看看怎么安排。",
            f"嗯嗯，{contact}你说得对，我再想想。",
        ]

        if "?" in content or "？" in content or "吗" in content:
            suggestions = [
                "可以的，没问题。",
                "让我想想，晚点回复你。",
                "好呀，具体什么时间？",
            ]
        elif any(w in content for w in ("谢谢", "感谢", "多谢")):
            suggestions = [
                "不客气～",
                "没事没事，应该的。",
                "哈哈，别客气！",
            ]
        elif any(w in content for w in ("吃饭", "约", "见面", "有空")):
            suggestions = [
                "好啊，什么时候方便？",
                "可以呀，你定时间吧。",
                "这周我有点忙，下周可以吗？",
            ]

        return suggestions[: config.generation.num_suggestions]

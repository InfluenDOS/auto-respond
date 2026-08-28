from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from auto_respond.chat.loader import load_conversation
from auto_respond.config import PROJECT_ROOT
from auto_respond.models import Conversation

logger = logging.getLogger(__name__)


@dataclass
class ChatEntry:
    id: str
    name: str
    file: Path
    enabled: bool = True


@dataclass
class ChatRegistry:
    entries: list[ChatEntry] = field(default_factory=list)

    def list_enabled(self) -> list[ChatEntry]:
        return [e for e in self.entries if e.enabled]

    def get(self, chat_id: str) -> ChatEntry:
        for entry in self.entries:
            if entry.id == chat_id:
                return entry
        raise KeyError(f"未找到指定的聊天记录: {chat_id}")

    def load(self, chat_id: str, user_name: str = "我") -> Conversation:
        entry = self.get(chat_id)
        if not entry.enabled:
            raise ValueError(f"聊天记录已禁用: {chat_id}")

        path = entry.file if entry.file.is_absolute() else PROJECT_ROOT / entry.file
        if not path.exists():
            raise FileNotFoundError(f"聊天记录文件不存在: {path}")

        conversation = load_conversation(path, user_name=user_name)
        if not conversation.contact:
            conversation.contact = entry.name
        return conversation

    def load_all_enabled(self, user_name: str = "我") -> list[Conversation]:
        conversations = []
        for entry in self.list_enabled():
            try:
                conversations.append(self.load(entry.id, user_name))
            except FileNotFoundError:
                logger.warning("跳过缺失文件: %s", entry.file)
        return conversations


def load_chat_registry(manifest_path: Path | None = None) -> ChatRegistry:
    from auto_respond.config import CONFIG_DIR

    manifest = manifest_path or CONFIG_DIR / "chats.yaml"
    if not manifest.exists():
        manifest = CONFIG_DIR / "chats.example.yaml"
        logger.warning("未找到 chats.yaml，使用 chats.example.yaml")

    data = _load_yaml(manifest)

    entries = []
    for item in data.get("chats", []):
        entries.append(
            ChatEntry(
                id=item["id"],
                name=item.get("name", item["id"]),
                file=Path(item["file"]),
                enabled=item.get("enabled", True),
            )
        )

    return ChatRegistry(entries=entries)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

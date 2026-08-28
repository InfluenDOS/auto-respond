from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from auto_respond.models import ChatMessage, Conversation

_LINE_PATTERN = re.compile(
    r"^(?P<sender>[^:]+?)\s*[:：]\s*(?P<content>.+)$"
)


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _mark_self(messages: list[ChatMessage], user_name: str) -> list[ChatMessage]:
    aliases = {user_name, "我", "自己", "Me", "me"}
    for msg in messages:
        msg.is_self = msg.sender in aliases
    return messages


def load_from_text(text: str, contact: str = "", user_name: str = "我") -> Conversation:
    messages: list[ChatMessage] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = _LINE_PATTERN.match(line)
        if not match:
            continue
        sender = match.group("sender").strip()
        content = match.group("content").strip()
        messages.append(ChatMessage(sender=sender, content=content))

    if not contact and messages:
        for msg in reversed(messages):
            if msg.sender != user_name and msg.sender not in ("我", "自己"):
                contact = msg.sender
                break

    _mark_self(messages, user_name)
    return Conversation(contact=contact, messages=messages)


def load_from_json(path: Path, user_name: str = "我") -> Conversation:
    data = json.loads(path.read_text(encoding="utf-8"))
    contact = data.get("contact", "")
    messages = []
    for item in data.get("messages", []):
        messages.append(
            ChatMessage(
                sender=item["sender"],
                content=item["content"],
                timestamp=_parse_timestamp(item.get("time")),
            )
        )
    _mark_self(messages, user_name)
    return Conversation(contact=contact, messages=messages)


def load_conversation(path: Path, user_name: str = "我") -> Conversation:
    if path.suffix.lower() == ".json":
        return load_from_json(path, user_name)
    return load_from_text(path.read_text(encoding="utf-8"), user_name=user_name)


def load_from_paste(user_name: str = "我") -> Conversation:
    print("请粘贴聊天记录（格式：发送者: 消息内容），输入空行结束：\n")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip() and lines:
            break
        lines.append(line)
    return load_from_text("\n".join(lines), user_name=user_name)

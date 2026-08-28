from __future__ import annotations

from auto_respond.config import AppConfig
from auto_respond.models import Conversation


def build_context(conversation: Conversation, config: AppConfig) -> str:
    messages = conversation.messages[-config.generation.max_context_messages :]
    lines = []
    for msg in messages:
        role = config.user_name if msg.is_self else msg.sender
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def build_system_prompt(config: AppConfig) -> str:
    return (
        "你是一个微信聊天回复助手。根据聊天记录，帮用户生成合适的回复建议。\n"
        f"回复风格：{config.generation.style}\n"
        f"语言：{config.generation.language}\n"
        "要求：\n"
        "1. 回复要贴合上下文，自然得体\n"
        "2. 每条建议长度适中，像真实微信消息（通常 1-3 句话）\n"
        "3. 提供不同语气或策略的选项（如简洁/热情/委婉等）\n"
        "4. 只输出回复内容本身，不要加引号或编号说明"
    )


def build_user_prompt(conversation: Conversation, config: AppConfig) -> str:
    context = build_context(conversation, config)
    contact = conversation.contact or "对方"
    last = conversation.last_message

    prompt = f"以下是我与「{contact}」的聊天记录：\n\n{context}\n\n"
    if last and not last.is_self:
        prompt += f"对方最新消息：{last.content}\n\n"
    prompt += f"请生成 {config.generation.num_suggestions} 条不同的回复建议，每条单独一行，用 --- 分隔。"
    return prompt

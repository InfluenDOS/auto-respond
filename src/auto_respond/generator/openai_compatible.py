from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request

from auto_respond.config import AppConfig
from auto_respond.context import build_system_prompt, build_user_prompt
from auto_respond.generator.base import ReplyGenerator
from auto_respond.models import Conversation

logger = logging.getLogger(__name__)


class OpenAICompatibleGenerator(ReplyGenerator):
    """支持 OpenAI / DeepSeek / 其他兼容 API 的生成器。"""

    def generate(self, conversation: Conversation, config: AppConfig) -> list[str]:
        if not config.llm.api_key:
            raise ValueError(
                "未配置 API Key。请在 config.yaml 中设置 llm.api_key，"
                "或设置环境变量 OPENAI_API_KEY"
            )

        system_prompt = build_system_prompt(config)
        user_prompt = build_user_prompt(conversation, config)

        payload = {
            "model": config.llm.model,
            "temperature": config.llm.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        url = config.llm.base_url.rstrip("/") + "/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.llm.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API 请求失败 ({exc.code}): {body}") from exc

        content = data["choices"][0]["message"]["content"]
        return _parse_suggestions(content, config.generation.num_suggestions)


def _parse_suggestions(text: str, max_count: int) -> list[str]:
    parts = [p.strip() for p in text.split("---") if p.strip()]
    if len(parts) <= 1:
        parts = [line.strip() for line in text.splitlines() if line.strip()]
        parts = [re.sub(r"^\d+[\.\)、]\s*", "", p) for p in parts]

    cleaned = []
    for part in parts:
        part = re.sub(r"^[\-\*•]\s*", "", part)
        part = part.strip("\"'「」")
        if part:
            cleaned.append(part)
    return cleaned[:max_count]

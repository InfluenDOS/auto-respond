from __future__ import annotations

import re
import time
from dataclasses import dataclass

from auto_respond.config import AppConfig, Rule, RulesConfig


@dataclass
class IncomingMessage:
    sender_id: str
    sender_name: str
    content: str
    is_group: bool = False
    room_id: str = ""


@dataclass
class MatchResult:
    rule: Rule
    reply: str


class RulesEngine:
    def __init__(self, app_config: AppConfig, rules_config: RulesConfig) -> None:
        self.app_config = app_config
        self.rules = [r for r in rules_config.rules if r.enabled]
        self._last_reply: dict[tuple[str, str], float] = {}

    def _is_allowed_sender(self, message: IncomingMessage) -> bool:
        sender_key = message.room_id if message.is_group else message.sender_id

        if self.app_config.blacklist:
            for blocked in self.app_config.blacklist:
                if blocked in (message.sender_id, message.sender_name, message.room_id):
                    return False

        if self.app_config.whitelist:
            return any(
                allowed in (message.sender_id, message.sender_name, message.room_id)
                for allowed in self.app_config.whitelist
            )

        return True

    def _matches(self, rule: Rule, content: str) -> bool:
        if rule.match_type == "exact":
            return content == rule.pattern
        if rule.match_type == "contains":
            return rule.pattern in content
        if rule.match_type == "regex":
            return bool(re.search(rule.pattern, content))
        return False

    def _cooldown_ok(self, rule: Rule, sender_key: str) -> bool:
        cooldown = rule.cooldown if rule.cooldown is not None else self.app_config.default_cooldown
        last = self._last_reply.get((rule.name, sender_key), 0)
        return time.time() - last >= cooldown

    def match(self, message: IncomingMessage) -> MatchResult | None:
        if not self._is_allowed_sender(message):
            return None

        sender_key = message.room_id if message.is_group else message.sender_id

        for rule in self.rules:
            if rule.senders and message.sender_id not in rule.senders:
                if message.sender_name not in rule.senders:
                    continue

            if not self._matches(rule, message.content):
                continue

            if not self._cooldown_ok(rule, sender_key):
                continue

            reply = rule.reply.format(sender=message.sender_name)
            self._last_reply[(rule.name, sender_key)] = time.time()
            return MatchResult(rule=rule, reply=reply)

        return None

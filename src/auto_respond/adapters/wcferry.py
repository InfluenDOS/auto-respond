from __future__ import annotations

import logging
import sys
from collections.abc import Callable

from auto_respond.adapters.base import WeChatAdapter
from auto_respond.rules import IncomingMessage

logger = logging.getLogger(__name__)


class WcferryAdapter(WeChatAdapter):
    """WeChatFerry 适配器，连接 PC 版微信。"""

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise RuntimeError("WeChatFerry 仅支持 Windows 系统")

        try:
            from wcferry import Wcf, WxMsg  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError(
                "请先安装 wcferry: pip install wcferry"
            ) from exc

        self._Wcf = Wcf
        self._WxMsg = WxMsg
        self._wcf: Wcf | None = None
        self._on_message: Callable[[IncomingMessage], None] | None = None

    def start(self, on_message: Callable[[IncomingMessage], None]) -> None:
        self._on_message = on_message
        self._wcf = self._Wcf()

        def _handler(msg: object, wcf: object) -> None:
            wx_msg = msg  # WxMsg
            if wx_msg.type != 1:  # 仅处理文本消息
                return
            if wx_msg.from_self():
                return

            is_group = wx_msg.from_group()
            sender_id = wx_msg.sender if is_group else wx_msg.sender
            sender_name = wcf.get_alias(sender_id) or sender_id

            message = IncomingMessage(
                sender_id=sender_id,
                sender_name=sender_name,
                content=wx_msg.content.strip(),
                is_group=is_group,
                room_id=wx_msg.roomid if is_group else "",
            )
            if self._on_message:
                self._on_message(message)

        self._wcf.enable_receiving_msg()
        logger.info("WeChatFerry 已连接，正在监听消息...")

        while self._wcf.is_receiving_msg():
            try:
                msg = self._wcf.get_msg()
                _handler(msg, self._wcf)
            except Exception:
                logger.exception("处理消息时出错")

    def send_text(self, target: str, content: str, is_group: bool = False) -> bool:
        if not self._wcf:
            return False
        try:
            self._wcf.send_text(content, target)
            return True
        except Exception:
            logger.exception("发送消息失败: target=%s", target)
            return False

    def stop(self) -> None:
        if self._wcf:
            self._wcf.cleanup()
            self._wcf = None

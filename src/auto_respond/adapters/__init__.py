from auto_respond.adapters.base import WeChatAdapter
from auto_respond.adapters.mock import MockAdapter

__all__ = ["WeChatAdapter", "MockAdapter"]


def create_adapter(adapter_type: str) -> WeChatAdapter:
    if adapter_type == "mock":
        return MockAdapter()
    if adapter_type == "wcferry":
        from auto_respond.adapters.wcferry import WcferryAdapter

        return WcferryAdapter()
    raise ValueError(f"未知适配器类型: {adapter_type}")

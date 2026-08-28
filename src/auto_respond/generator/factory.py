from auto_respond.config import AppConfig
from auto_respond.generator.base import ReplyGenerator
from auto_respond.generator.mock import MockGenerator
from auto_respond.generator.openai_compatible import OpenAICompatibleGenerator


def create_generator(config: AppConfig) -> ReplyGenerator:
    provider = config.llm.provider
    if provider == "mock":
        return MockGenerator()
    if provider == "openai_compatible":
        return OpenAICompatibleGenerator()
    raise ValueError(f"未知 LLM provider: {provider}")

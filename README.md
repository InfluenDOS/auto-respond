# auto-respond

根据微信聊天记录，智能生成可行的回复建议。你自行挑选、复制后发送，**不会自动回复**。

## 它能做什么

1. 读取聊天记录（文件、粘贴、JSON）
2. 分析对话上下文
3. 生成多条不同风格的回复建议
4. 你手动复制喜欢的回复发到微信

## 快速开始

```bash
git clone https://github.com/InfluenDOS/auto-respond.git
cd auto-respond
pip install -r requirements.txt

# 复制配置
copy config\config.example.yaml config\config.yaml

# 设置 API Key（使用 OpenAI / DeepSeek 等）
set OPENAI_API_KEY=sk-xxx

# Mock 模式测试（无需 API Key）
python -m auto_respond suggest --mock --chat examples/chat.txt

# 使用真实 LLM 生成
python -m auto_respond suggest --chat examples/chat.txt

# 交互式粘贴聊天记录
python -m auto_respond suggest --paste
```

## 聊天记录格式

### 文本格式（.txt）

```
张三: 在吗？
我: 在的，怎么了
张三: 周末有空吗，想约你吃饭
```

### JSON 格式（.json）

```json
{
  "contact": "张三",
  "messages": [
    {"sender": "张三", "content": "周末有空吗？", "time": "2026-08-28 10:00"},
    {"sender": "我", "content": "有空，怎么了", "time": "2026-08-28 10:01"}
  ]
}
```

## 配置说明

| 字段 | 说明 |
|------|------|
| `user_name` | 你在聊天中的名字，默认「我」 |
| `llm.provider` | `mock`（测试）或 `openai_compatible` |
| `llm.api_key` | API 密钥，支持 `${OPENAI_API_KEY}` 环境变量 |
| `llm.base_url` | API 地址，兼容 OpenAI 格式的服务均可 |
| `llm.model` | 模型名称 |
| `generation.num_suggestions` | 生成几条建议 |
| `generation.style` | 回复风格描述 |

### 使用 DeepSeek

```yaml
llm:
  provider: openai_compatible
  api_key: ${DEEPSEEK_API_KEY}
  base_url: https://api.deepseek.com/v1
  model: deepseek-chat
```

## 项目结构

```
auto-respond/
├── config/              # 配置文件
├── examples/            # 示例聊天记录
├── src/auto_respond/
│   ├── chat/            # 聊天记录加载
│   ├── generator/       # LLM 回复生成
│   ├── context.py       # 上下文构建
│   └── app.py           # CLI 入口
└── requirements.txt
```

## 如何获取聊天记录

目前支持手动导入：

1. **复制粘贴**：从微信选中对话内容，保存为文本或直接用 `--paste`
2. **手动整理**：按 `发送者: 内容` 格式写入 `.txt` 文件
3. **JSON 导出**：适合程序化整理的历史记录

> 后续可扩展：对接 WeChatFerry 自动拉取最近消息、解析微信导出文件等。

## License

MIT

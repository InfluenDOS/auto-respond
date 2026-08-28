# auto-respond

微信消息自动回复工具。根据可配置的规则，自动回复指定的微信私聊或群聊消息。

## 功能

- 基于关键词、正则表达式、发送者匹配规则
- 支持精确匹配、包含匹配、正则匹配
- 可配置白名单/黑名单（联系人、群聊）
- 支持冷却时间，避免重复回复
- 可插拔的微信适配器（WeChatFerry / Mock 测试模式）

## 环境要求

- Python 3.10+
- Windows 系统（WeChatFerry 需要 PC 版微信）
- 已安装并登录 [微信 PC 版](https://weixin.qq.com/)

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/InfluenDOS/auto-respond.git
cd auto-respond

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS（仅 Mock 模式）

# 安装依赖
pip install -r requirements.txt

# 复制并编辑配置
copy config\config.example.yaml config\config.yaml
copy config\rules.example.yaml config\rules.yaml

# 启动（Mock 模式，用于测试规则）
python -m auto_respond --mock

# 启动（WeChatFerry 模式，连接真实微信）
python -m auto_respond
```

## 配置说明

### config.yaml

| 字段 | 说明 |
|------|------|
| `adapter` | 适配器类型：`wcferry` 或 `mock` |
| `whitelist` | 仅对这些联系人/群生效（空=全部） |
| `blacklist` | 忽略这些联系人/群 |
| `default_cooldown` | 默认冷却时间（秒） |
| `log_level` | 日志级别 |

### rules.yaml

每条规则包含：

| 字段 | 说明 |
|------|------|
| `name` | 规则名称 |
| `enabled` | 是否启用 |
| `match_type` | `exact` / `contains` / `regex` |
| `pattern` | 匹配内容 |
| `reply` | 回复文本（支持 `{sender}` 占位符） |
| `senders` | 限定发送者（可选） |
| `cooldown` | 该规则冷却时间（可选） |

示例：

```yaml
rules:
  - name: 问候回复
    enabled: true
    match_type: contains
    pattern: 你好
    reply: "你好 {sender}，我现在不在，稍后回复你。"

  - name: 价格咨询
    enabled: true
    match_type: regex
    pattern: "(价格|多少钱|报价)"
    reply: "感谢咨询！请查看我们的价目表：https://example.com/pricing"
    cooldown: 300
```

## 项目结构

```
auto-respond/
├── config/           # 配置文件
├── src/auto_respond/ # 核心代码
│   ├── adapters/     # 微信连接适配器
│   ├── handlers/     # 消息处理器
│   ├── app.py        # 应用入口
│   ├── config.py     # 配置加载
│   └── rules.py      # 规则引擎
└── requirements.txt
```

## 注意事项

> **重要**：个人微信没有官方开放 API，本项目使用 [WeChatFerry](https://github.com/lich0821/WeChatFerry) 通过 PC 客户端 Hook 实现消息收发。使用前请了解相关风险，建议仅用于个人账号的自动化场景。

- 请勿用于 spam 或违规用途
- 建议先在 `--mock` 模式下测试规则
- 微信版本更新可能导致 Hook 失效，请关注 WeChatFerry 更新

## License

MIT

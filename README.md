# Seed 2.0 Pro MCP Server

基于 [FastMCP](https://github.com/modelcontextprotocol/python-sdk) 的 Model Context Protocol 服务器，封装字节跳动 **Seed 2.0 Pro** 旗舰推理模型，通过 [API易](https://api.apiyi.com) 的 OpenAI 兼容接口调用。

## ✨ 特性

- 🧠 **Seed 2.0 Pro**（`seed-2-0-pro-260328`）：字节最新旗舰推理模型
  - AIME 2025 = 98.3
  - Codeforces = 3020
  - SWE-Bench = 76.5%
  - VideoMME = 89.5
- 🛠️ 暴露三个 MCP 工具
  - `seed_chat` — 纯文本对话/推理（数学、代码、长链思考）
  - `seed_vision` — 多模态：图片本地路径或 URL 输入
  - `seed_tools` — Function Calling / Agent 工具调用
- 🔌 OpenAI 兼容协议，端点走 `https://api.apiyi.com/v1`
- 🪟 内置 `start.bat`，方便在 Windows 下被 Cursor / Claude Desktop 拉起（规避部分企业 DLP 软件对 Python 入口的拦截）

## 📦 安装

```bash
pip install -r requirements.txt
```

## ⚙️ 环境变量

| 变量 | 必须 | 默认值 | 说明 |
|------|------|--------|------|
| `APIYI_API_KEY` | ✅ | — | API易 密钥 |
| `APIYI_BASE_URL` |  | `https://api.apiyi.com/v1` | OpenAI 兼容端点 |
| `SEED_MODEL` |  | `seed-2-0-pro-260328` | 默认模型 |
| `SEED_TEMPERATURE` |  | `0.6` | 默认温度 |
| `SEED_MAX_TOKENS` |  | `16384` | 默认最大输出 tokens |
| `SEED_TIMEOUT` |  | `1800` | 请求超时（秒） |

## 🚀 使用

### Windows + Cursor（通过 start.bat 启动）

```json
{
  "mcpServers": {
    "seed": {
      "command": "cmd",
      "args": ["/c", "D:\\path\\to\\seed-mcp-server\\start.bat"],
      "env": {
        "APIYI_API_KEY": "sk-YOUR_API_KEY_HERE",
        "APIYI_BASE_URL": "https://api.apiyi.com/v1",
        "SEED_MODEL": "seed-2-0-pro-260328",
        "SEED_TEMPERATURE": "0.6",
        "SEED_MAX_TOKENS": "16384",
        "SEED_TIMEOUT": "1800",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

### 直接调 python（无 DLP 拦截的环境）

```json
{
  "mcpServers": {
    "seed": {
      "command": "python",
      "args": ["D:/path/to/seed-mcp-server/server.py"],
      "env": {
        "APIYI_API_KEY": "sk-YOUR_API_KEY_HERE"
      }
    }
  }
}
```

## 🛠️ 可用工具

### 1. `seed_chat` — 纯文本推理

适合：数学证明、代码生成、复杂推理、长链思考。

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_prompt` | str | 用户提示词（必填） |
| `system_prompt` | str? | 系统提示词（可选） |
| `model` | str? | 默认 `seed-2-0-pro-260328` |
| `temperature` | float? | `0`~`2`，默认 `0.6` |
| `max_tokens` | int? | 默认 `16384` |

### 2. `seed_vision` — 多模态图像理解

适合：设计稿 → HTML/CSS、图表分析、视觉推理。

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_prompt` | str | 关于图片的问题或指令 |
| `images` | list[str] | 每项可以是**本地路径**（自动 base64 编码）或 **HTTP(S) URL** |
| `detail` | "low" \| "high" | 默认 `"high"` |
| `max_tokens` | int? | 默认 `16384` |

### 3. `seed_tools` — Function Calling / Agent

适合：需要模型决定调用哪些函数的 Agent 场景。

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_prompt` | str | 用户请求 |
| `tools` | list[dict] | OpenAI 格式 tools 数组（function schema） |
| `tool_choice` | "auto" \| "none" \| "required" | 默认 `"auto"` |

返回：JSON 字符串，包含 `content` 与 `tool_calls`（含函数名与参数）。

## 📁 目录结构

```
seed-mcp-server/
├── server.py          # FastMCP 服务实现
├── start.bat          # Windows 启动脚本
├── requirements.txt   # mcp + openai
└── README.md
```

## 🔗 相关链接

- **GitHub**: <https://github.com/2799662352/seed-mcp-server>
- **API易**: <https://api.apiyi.com/>
- **Model Context Protocol**: <https://modelcontextprotocol.io>
- **FastMCP Python SDK**: <https://github.com/modelcontextprotocol/python-sdk>

## 📄 许可证

MIT

"""
Seed 2.0 Pro MCP Server (FastMCP)
==================================
基于 FastMCP 的 MCP 服务器，调用字节跳动 Seed 2.0 Pro 旗舰推理模型
通过 API易 (apiyi.com) 的 OpenAI 兼容接口

模型: seed-2-0-pro-260328
端点: https://api.apiyi.com/v1
"""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from openai import OpenAI

API_KEY = os.getenv("APIYI_API_KEY", "").strip()
BASE_URL = os.getenv("APIYI_BASE_URL", "https://api.apiyi.com/v1").strip()
DEFAULT_MODEL = os.getenv("SEED_MODEL", "seed-2-0-pro-260328").strip()
DEFAULT_TEMPERATURE = float(os.getenv("SEED_TEMPERATURE", "0.6"))
DEFAULT_MAX_TOKENS = int(os.getenv("SEED_MAX_TOKENS", "16384"))
REQUEST_TIMEOUT = float(os.getenv("SEED_TIMEOUT", "1800"))

if not API_KEY:
    print(
        "[seed-mcp] ERROR: 未设置环境变量 APIYI_API_KEY",
        file=sys.stderr,
    )
    sys.exit(1)

print(
    "[seed-mcp] Server starting with config:\n"
    f"  - base_url       = {BASE_URL}\n"
    f"  - default_model  = {DEFAULT_MODEL}\n"
    f"  - max_tokens     = {DEFAULT_MAX_TOKENS}\n"
    f"  - temperature    = {DEFAULT_TEMPERATURE}\n"
    f"  - timeout        = {REQUEST_TIMEOUT}s",
    file=sys.stderr,
)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=REQUEST_TIMEOUT)

mcp = FastMCP(
    name="seed-mcp",
    instructions=(
        "字节跳动 Seed 2.0 Pro 旗舰推理模型。"
        "擅长复杂推理、数学证明、编程、Agent 工作流、多模态理解。"
        "AIME 2025=98.3，Codeforces=3020，SWE-Bench=76.5%，VideoMME=89.5。"
    ),
)


IMAGE_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


def _image_to_data_url(path_or_url: str) -> str:
    """将本地图片转 data URL，URL 原样返回"""
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url

    p = Path(path_or_url)
    if not p.exists():
        raise FileNotFoundError(f"图片文件不存在: {path_or_url}")

    mime = IMAGE_MIME.get(p.suffix.lower(), "application/octet-stream")
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


@mcp.tool()
def seed_chat(
    user_prompt: str,
    system_prompt: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    使用 Seed 2.0 Pro 进行纯文本对话推理。

    适合：数学证明、代码生成、复杂推理、长链思考。

    Args:
        user_prompt: 用户提示词（必填）
        system_prompt: 系统提示词（可选，用于设定角色或行为）
        model: 模型名称，默认 seed-2-0-pro-260328
        temperature: 温度 0-2，默认 0.6
        max_tokens: 最大输出 tokens，默认 16384
    """
    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    resp = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature if temperature is not None else DEFAULT_TEMPERATURE,
        max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
    )
    return resp.choices[0].message.content or ""


@mcp.tool()
def seed_vision(
    user_prompt: str,
    images: list[str],
    system_prompt: str | None = None,
    model: str | None = None,
    detail: str = "high",
    max_tokens: int | None = None,
) -> str:
    """
    使用 Seed 2.0 Pro 的多模态能力理解图片。

    适合：图像转代码（设计稿→HTML/CSS）、图表分析、视觉推理。

    Args:
        user_prompt: 关于图片的问题或指令
        images: 图片列表，每项可以是
                - 本地路径（自动 base64 编码，如 "D:/photo.jpg"）
                - HTTP/HTTPS URL（如 "https://example.com/x.png"）
        system_prompt: 系统提示词（可选）
        model: 模型名称，默认 seed-2-0-pro-260328
        detail: 图片细节级别 "low" | "high"，默认 high
        max_tokens: 最大输出 tokens，默认 16384
    """
    if not images:
        raise ValueError("images 不能为空，至少需要一张图片")

    content: list[dict[str, Any]] = [{"type": "text", "text": user_prompt}]
    for img in images:
        url = _image_to_data_url(img)
        content.append(
            {"type": "image_url", "image_url": {"url": url, "detail": detail}}
        )

    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": content})

    resp = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
    )
    return resp.choices[0].message.content or ""


@mcp.tool()
def seed_tools(
    user_prompt: str,
    tools: list[dict[str, Any]],
    system_prompt: str | None = None,
    model: str | None = None,
    tool_choice: str = "auto",
) -> str:
    """
    使用 Seed 2.0 Pro 的工具调用 / Function Calling 能力。

    适合：Agent 工作流、需要模型决定调用哪些函数的场景。

    Args:
        user_prompt: 用户请求
        tools: OpenAI 格式的 tools 数组，每项形如:
               {
                 "type": "function",
                 "function": {
                   "name": "search_flights",
                   "description": "...",
                   "parameters": {...JSON Schema...}
                 }
               }
        system_prompt: 系统提示词（可选）
        model: 模型名称，默认 seed-2-0-pro-260328
        tool_choice: "auto" | "none" | "required"，默认 auto
    """
    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    resp = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
    )
    msg = resp.choices[0].message
    return json.dumps(
        {
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in (msg.tool_calls or [])
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")

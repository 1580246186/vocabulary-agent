"""Agent — 扫描 SKILL.md 发现工具，通过 LLM function-calling 自主编排任务。

渐进式披露：
  1. 初始只加载 YAML 摘要（工具名 + 一句话描述 + 参数列表）
  2. LLM 决定调用某工具 → 首次调用时先返回完整 SKILL.md 正文
  3. LLM 阅读文档后重新调用 → Agent 执行脚本返回真实结果
"""

import importlib
import json
import re
from pathlib import Path

import yaml
from openai import OpenAI

from lib.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, MAX_RETRIES

SKILLS_DIR = Path(__file__).parent / "skills"
MAX_TURNS = 20


# ── 工具发现 ──────────────────────────────────────────

def discover_skills() -> tuple[list[dict], dict[str, str], dict[str, str]]:
    """扫描 skills/*/SKILL.md，返回 (工具schema, 名称→模块路径, 名称→完整正文)。"""
    schemas = []
    modules = {}
    docs = {}

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        md = skill_dir / "SKILL.md"
        if not md.exists():
            continue

        full_text = md.read_text(encoding="utf-8")
        frontmatter, body = _parse_frontmatter(full_text)
        if not frontmatter:
            continue

        name = frontmatter.get("name", skill_dir.name)
        desc = frontmatter.get("description", "")
        params_meta = frontmatter.get("parameters", {})

        # 构建 OpenAI function-calling 参数定义
        properties = {}
        required = []
        for pname, pinfo in params_meta.items():
            properties[pname] = {
                "type": pinfo.get("type", "string"),
                "description": pinfo.get("description", ""),
            }
            if pinfo.get("required"):
                required.append(pname)

        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

        module_path = f"skills.{skill_dir.name}.scripts.run"
        schemas.append(schema)
        modules[name] = module_path
        docs[name] = body.strip() if body else ""

    return schemas, modules, docs


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 YAML 前置元数据，返回 (元数据字典, 正文)。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", text, re.DOTALL)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2).strip()


# ── 系统提示词 ────────────────────────────────────────

def _load_system_prompt(tool_schemas: list[dict]) -> str:
    """加载基础角色提示 + 动态注入已发现工具列表。"""
    path = SKILLS_DIR.parent / "prompts" / "agent_system.md"
    base = path.read_text(encoding="utf-8") if path.exists() else "你是一个自动化任务处理 Agent。"

    catalog = "## 可用工具\n\n"
    for t in tool_schemas:
        f = t["function"]
        catalog += f"- **{f['name']}**: {f['description']}\n"

    return base + "\n\n" + catalog


# ── Agent 主循环 ──────────────────────────────────────

def run(task: str) -> str:
    """启动 Agent，根据任务描述自主调用工具直到完成。"""
    tool_schemas, modules, docs = discover_skills()
    if not tool_schemas:
        return "未发现任何 Skill。"

    print(f"发现 {len(tool_schemas)} 个工具: {[t['function']['name'] for t in tool_schemas]}")

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    messages = [
        {"role": "system", "content": _load_system_prompt(tool_schemas)},
        {"role": "user", "content": task},
    ]

    disclosed = set()  # 已披露完整文档的工具名称集合

    for turn in range(MAX_TURNS):
        print(f"\n--- 第 {turn + 1} 轮 ---")

        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tool_schemas,
            tool_choice="auto",
            max_tokens=4096,
        )
        msg = resp.choices[0].message

        # LLM 返回纯文本，没有调用工具
        if not msg.tool_calls:
            text = msg.content or ""
            if text:
                print(f"[Agent] {text[:500]}")
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", "content": "请继续完成任务，或调用 finish 汇报结果。"})
            continue

        # 记录 LLM 的工具调用
        assistant_msg = {
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        }
        messages.append(assistant_msg)

        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}

            print(f"[工具] {name}({json.dumps(args, ensure_ascii=False)[:200]})")

            # ── 渐进式披露：首次调用先返回文档，不执行 ──
            first_use = name not in disclosed and bool(docs.get(name))
            if first_use:
                disclosed.add(name)
                print(f"[披露] 首次使用 {name}，返回完整文档 ({len(docs[name])} 字)")
                result_str = json.dumps({
                    "_disclosure": True,
                    "skill": name,
                    "docs": docs[name],
                    "message": "请阅读以上详细文档，确认参数无误后重新调用此工具。",
                }, ensure_ascii=False)
            else:
                try:
                    mod = importlib.import_module(modules[name])
                    result = mod.run(**args)
                    result_str = json.dumps(result, ensure_ascii=False, default=str)
                    if len(result_str) > 3000:
                        result_str = result_str[:3000] + "...(已截断)"
                    print(f"[结果] {result_str[:300]}")
                except Exception as e:
                    result_str = json.dumps({"error": str(e)}, ensure_ascii=False)
                    print(f"[错误] {e}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_str,
            })

            if name == "finish":
                print(f"\n=== Agent 完成: {args.get('summary', '')} ===")
                return args.get("summary", "完成。")

    return "已达最大轮次，Agent 停止。"

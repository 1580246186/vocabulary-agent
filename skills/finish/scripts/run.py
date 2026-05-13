"""Skill: 标记任务完成。"""

def run(summary: str) -> dict:
    """Agent 调用此工具后退出循环。"""
    return {"status": "finished", "summary": summary}

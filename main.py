"""词汇处理 Agent — 入口。

用法:
    python main.py <input.docx> [output.xlsx]
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from agent import run


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <input.docx> [output.xlsx]")
        sys.exit(1)

    input_path = Path(sys.argv[1]).resolve()
    if not input_path.exists():
        print(f"[错误] 找不到文件: {input_path}")
        sys.exit(1)

    output_path = sys.argv[2] if len(sys.argv) > 2 else "vocabulary_output.xlsx"

    task = f"请处理词汇文档：\n输入文件：{input_path}\n输出文件：{output_path}\n请按 读取→生成→完成 的顺序执行。"

    print(f"输入: {input_path}")
    print(f"输出: {output_path}")
    print()

    result = run(task)
    print(f"\n{result}")


if __name__ == "__main__":
    main()

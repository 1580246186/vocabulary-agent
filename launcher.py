"""启动器：交互式获取输入输出路径，然后启动 Agent。"""

import sys
from pathlib import Path


def main():
    print("=" * 44)
    print("  Vocabulary Agent")
    print("=" * 44)
    print()

    # 输入文件
    input_path = _get_input()

    # 输出文件
    output_path = input("输出 Excel 路径（回车默认 vocabulary_output.xlsx）: ").strip().strip('"')
    if not output_path:
        output_path = "vocabulary_output.xlsx"

    print()
    print(f"输入: {input_path}")
    print(f"输出: {output_path}")
    print()
    print("正在运行，请稍候...")
    print()

    from agent import run
    task = f"请处理词汇文档：\n输入文件：{input_path}\n输出文件：{output_path}\n请按 读取→生成→完成 的顺序执行。"
    result = run(task)
    print(f"\n{result}")
    input("按回车退出...")


def _get_input() -> Path:
    # 支持命令行参数（拖拽文件）
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if p.exists():
            return p.resolve()
        print(f"[错误] 文件不存在: {p}")

    while True:
        raw = input("输入 Word 文档路径（或拖拽文件到此处）: ").strip().strip('"')
        if not raw:
            print("路径不能为空。")
            continue
        p = Path(raw)
        if p.exists():
            return p.resolve()
        print(f"[错误] 文件不存在: {raw}")


if __name__ == "__main__":
    main()

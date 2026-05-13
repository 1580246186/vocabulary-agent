# Vocabulary Agent

基于 LLM 驱动的英语词汇处理 Agent，将 Word 文档中的词汇表自动转换为包含例句和选词填空练习的 Excel 文件。

## 功能

- 读取 Word 文档（.docx），自动解析 `单词 词性 释义` 格式的词汇条目
- 智能过滤错位单词（如在 C 段落中误放的 A 开头单词）
- 精简中文翻译（去括号、去多余标点）
- 调用 LLM 为每个单词生成英文例句和中文翻译
- 每 10 个单词一组，生成选词填空练习题（单词表有序，题目乱序）
- 输出纯文本 Excel 文件（词汇表 + 选词填空两个 Sheet）

## 项目结构

```
├── agent.py                     # Agent 核心：工具发现 + LLM 决策循环
├── main.py                      # 入口
├── skills/                      # Skill 定义（标准格式，可迁移到 Claude Code）
│   ├── read_vocabulary/         #   读取 Word 文档
│   │   ├── SKILL.md             #     YAML 元数据 + Markdown 文档
│   │   └── scripts/run.py       #     实现脚本
│   ├── generate_exercise/       #   生成例句 + 选词填空 + 写入 Excel
│   │   ├── SKILL.md
│   │   ├── prompts/             #     本 skill 的 LLM prompt（自包含）
│   │   │   ├── sentence.md
│   │   │   └── cloze.md
│   │   └── scripts/run.py
│   └── finish/                  #   标记任务完成
│       ├── SKILL.md
│       └── scripts/run.py
├── prompts/
│   └── agent_system.md          # Agent 系统提示词（可编辑）
├── lib/
│   └── config.py                # 全局配置（LLM API、分组大小等）
└── requirements.txt
```

## 渐进式披露

Agent 采用渐进式披露（Progressive Disclosure）机制：

1. **Level 1 — 初始加载**：扫描 `skills/*/SKILL.md` 的 YAML 前置元数据，构建工具列表
2. **Level 2 — 首次调用**：LLM 决定使用某工具时，先返回该 SKILL.md 的完整正文供阅读
3. **Level 3 — 执行**：LLM 理解文档后重新调用，Agent 才真正执行脚本

## 安装

```bash
# 创建 conda 环境
conda create -n word2excel python=3.11 -y
conda activate word2excel

# 安装依赖
pip install -r requirements.txt
```

## 配置

设置环境变量（支持所有 OpenAI 兼容接口的 LLM）：

```bash
# 必填
set LLM_API_KEY=sk-your-key

# 可选（默认千问）
set LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
set LLM_MODEL=qwen-plus
```

支持的 LLM 提供商：

| 提供商 | LLM_BASE_URL | LLM_MODEL |
|--------|-------------|-----------|
| 千问 Qwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| 月之暗面 | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| 智谱 | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` |

## 使用

```bash
conda activate word2excel
python main.py vocabulary.docx output.xlsx
```

或双击 `run.bat`（Windows）。

## Word 文档格式

文档应为段落形式，每行格式：

```
单词 <Tab> 词性 <Tab> 中文释义
```

示例：
```
abandon	v.	放弃；遗弃
abbreviate	v.	缩写；缩短
```

- 单词按首字母顺序排列（所有 A 开头 → 所有 B 开头 → ...）
- 翻译过长换行会自动合并
- 段落标题（如单字母 "A"、"B"）自动跳过

## 输出

### 词汇表 Sheet

| 序号 | 单词 词性 中文释义 | 英文例句 | 例句翻译 | 组号 |
|------|-------------------|----------|----------|------|
| 1 | abandon v. 放弃;遗弃 | She abandoned her plan. | 她放弃了计划。 | 1 |

### 选词填空 Sheet

```
第 1 组
可选单词：abandon，abbreviate，abide，...

| 题号 | 题目（填空） | 答案 | 中文提示 |
|------|-------------|------|---------|
| 1 | They had to _____ the ship. | abandon | 放弃 |
```

## 添加新 Skill

在 `skills/` 下新建目录，放入 `SKILL.md`（含 YAML 前置元数据）和 `scripts/run.py`（实现函数）。Agent 启动时自动发现，无需修改任何现有代码。

## License

MIT

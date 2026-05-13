---
name: read_vocabulary
description: >
  读取 Word 文档，提取英语词汇表，自动过滤错位单词并精简中文翻译。
  单词按首字母顺序排列（A→B→C...），翻译换行会自动合并。
parameters:
  filepath:
    type: string
    description: Word 文档的完整路径（.docx 文件）
    required: true
---

# 读取词汇文档

从 Word 文档中解析词汇条目（Tab/空格分隔的 `单词 词性 释义` 格式），
过滤掉错位单词（如 C 段落中出现的 A 开头单词），精简中文翻译。

## 返回

```json
[
  {"word": "abandon", "pos": "v.", "translation": "放弃;遗弃", "first_letter": "a"},
  ...
]
```

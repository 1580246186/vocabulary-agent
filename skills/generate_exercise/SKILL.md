---
name: generate_exercise
description: >
  为词汇列表生成英文例句和选词填空练习题，写入 Excel 文件。
  将 read_vocabulary 返回的完整词汇列表传入即可。
parameters:
  words:
    type: array
    description: 词汇列表（read_vocabulary 的返回值），每个元素含 word/pos/translation/first_letter
    required: true
  output_path:
    type: string
    description: 输出的 Excel 文件路径，如 vocabulary_output.xlsx
    required: true
---

# 生成练习题

1. 调用 LLM 为每个单词生成英文例句 + 中文翻译
2. 按 10 个一组生成选词填空（单词表有序，题目乱序）
3. 写入 Excel：词汇表 Sheet + 选词填空 Sheet

## 返回

```json
{
  "filepath": "/path/to/output.xlsx",
  "words": 23,
  "groups": 3
}
```

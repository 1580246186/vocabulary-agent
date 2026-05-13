---
name: finish
description: 任务完成时调用此工具，汇报处理结果。
parameters:
  summary:
    type: string
    description: 任务完成总结，包括处理的单词数量、生成的文件路径等
    required: true
---

# 完成任务

所有步骤完成后调用此工具输出最终总结，Agent 收到后退出循环。

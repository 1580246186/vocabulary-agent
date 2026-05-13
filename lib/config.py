"""全局配置。

支持的 LLM 提供商（设置环境变量即可切换）：
    LLM_API_KEY   — API 密钥（必填）
    LLM_BASE_URL  — API 地址（默认千问）
    LLM_MODEL     — 模型名称（默认 qwen3-vl-plus）

常用预设：
    DeepSeek:  base_url=https://api.deepseek.com          model=deepseek-chat
    千问 Qwen:  base_url=https://dashscope.aliyuncs.com/compatible-mode/v1  model=qwen-plus
    月之暗面:   base_url=https://api.moonshot.cn/v1        model=moonshot-v1-8k
    智谱:      base_url=https://open.bigmodel.cn/api/paas/v4  model=glm-4
"""

import os

# OpenAI 兼容 API 配置
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen-plus")

# 处理参数
GROUP_SIZE = 10      # 每组单词数量
MAX_RETRIES = 3      # LLM 调用最大重试次数

# Excel 输出配置
OUTPUT_FILENAME = "vocabulary_output.xlsx"
VOCAB_SHEET = "词汇表"
CLOZE_SHEET = "选词填空"

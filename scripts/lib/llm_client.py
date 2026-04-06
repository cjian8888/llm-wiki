"""
LLM Client — 负责与大模型通信，执行结构化知识提取。
使用 OpenAI 兼容接口，支持 Kimi / OpenAI / 其他兼容服务。
"""

import json
import sys
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME


# ---------- 输出格式定义 ----------

class KnowledgeExtraction(BaseModel):
    summary: str
    """对原文的简洁摘要（2-4 句）"""

    key_claims: list[str]
    """原文中最值得记录的核心主张，每条一句话"""

    entities: list[str]
    """识别出的具名实体：人物、机构、模型、数据集、产品等"""

    concepts: list[str]
    """识别出的核心概念：方法论、技术思想、专业术语等"""


# ---------- 客户端初始化 ----------

_client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)

_SYSTEM_PROMPT = """\
你是一个严格的知识库管理员。你的任务是从用户提供的原始文档中提取结构化知识。

你必须只返回一个合法的 JSON 对象，不得包含任何额外的文字、注释或 markdown 代码块。
JSON 对象包含以下字段：

- summary (string)：对原文的简洁摘要，2-4 句话，提炼核心论点。
- key_claims (array of string)：原文中最重要的核心主张，每条一句话，通常 3-8 条。
- entities (array of string)：识别出的所有具名实体，包括人物、机构、模型名称、数据集、产品名等。
- concepts (array of string)：识别出的核心概念，包括方法论、技术思想、专业术语等。

输出示例：
{
  "summary": "本文介绍了 Transformer 架构中的注意力机制，证明其在 NLP 任务上优于 RNN。",
  "key_claims": [
    "自注意力机制可以并行计算，克服了 RNN 的顺序计算瓶颈",
    "多头注意力允许模型同时关注不同子空间的信息"
  ],
  "entities": ["Transformer", "BERT", "Google Brain", "WMT 2014"],
  "concepts": ["自注意力", "多头注意力", "位置编码", "编码器-解码器架构"]
}
"""


# ---------- 核心函数 ----------

def extract_knowledge(text: str) -> KnowledgeExtraction:
    """
    读取原始文本，调用 LLM 提取结构化知识。

    Args:
        text: 原始文档内容（来自 inbox/ 的文件）

    Returns:
        KnowledgeExtraction: 经 Pydantic 验证的结构化提取结果

    Raises:
        ValueError: LLM 返回内容无法解析为合法 JSON 或字段不符合预期
    """
    response = _client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"请提取以下文档的知识：\n\n{text}"},
        ],
        temperature=0.2,  # 低温度确保输出稳定、格式一致
    )

    raw = response.choices[0].message.content.strip()

    # 防御：剥离模型可能错误添加的 markdown 代码块
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 返回内容不是合法 JSON：{e}\n原始内容：{raw[:200]}") from e

    try:
        return KnowledgeExtraction(**data)
    except ValidationError as e:
        raise ValueError(f"LLM 返回 JSON 字段不符合预期：{e}") from e

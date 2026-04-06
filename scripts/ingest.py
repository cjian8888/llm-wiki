"""
Ingest Pipeline — 摄入管道主入口。

流程：
  1. 加载 inbox/ 源文件
  2. 调用 LLM 提取结构化知识
  3. 生成标准 wiki_nodes/source_summary/*.md
  4. 将源文件归档到 inbox/archived/
"""

import logging
import re
import shutil
import sys
from datetime import date
from pathlib import Path

# 将 scripts/ 加入路径，保证容器与本地均可导入
sys.path.insert(0, str(Path(__file__).parent))

from lib.llm_client import KnowledgeExtraction, extract_knowledge
from lib.loader import DocumentLoader

logger = logging.getLogger("ingest")

ROOT_DIR = Path(__file__).parent.parent
WIKI_NODES_DIR = ROOT_DIR / "wiki_nodes" / "source_summary"
ARCHIVED_DIR = ROOT_DIR / "inbox" / "archived"


# ---------- 工具函数 ----------

def _slugify(name: str) -> str:
    """将文件名转换为 kebab-case slug。"""
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "-", name)
    return name.strip("-")


def _render_wiki_node(slug: str, source_filename: str, extraction: KnowledgeExtraction) -> str:
    """将提取结果渲染为标准 Markdown wiki node。"""
    today = date.today().isoformat()

    # YAML Frontmatter
    tags_yaml = "\n".join(f"  - {t}" for t in (extraction.concepts[:3] if extraction.concepts else ["uncategorized"]))
    entities_yaml = "\n".join(f"  - \"{e}\"" for e in extraction.entities)
    concepts_yaml = "\n".join(f"  - \"{c}\"" for c in extraction.concepts)

    frontmatter = f"""\
---
id: "{slug}"
title: "{slug.replace('-', ' ').title()}"
type: source_summary
tags:
{tags_yaml}
created: "{today}"
updated: "{today}"
source_file: "inbox/{source_filename}"
source_url: ""
source_title: "{slug.replace('-', ' ').title()}"
source_author: ""
source_date: ""
source_count: 1
status: active
confidence: medium
related: []
---"""

    # 关键主张
    claims_md = "\n".join(f"- {claim}" for claim in extraction.key_claims)

    # 实体与概念
    entities_md = "、".join(f"`{e}`" for e in extraction.entities) if extraction.entities else "（未识别）"
    concepts_md = "、".join(f"[[concept/{_slugify(c)}|{c}]]" for c in extraction.concepts) if extraction.concepts else "（未识别）"

    body = f"""
# {slug.replace('-', ' ').title()}

{extraction.summary}

## 关键主张

{claims_md}

## 实体

{entities_md}

## 核心概念

{concepts_md}

## 开放问题 / 知识盲区

- [ ] （待 Lint 阶段补充）

## 参考来源

- 原始文件：`inbox/{source_filename}`
"""

    return frontmatter + body


# ---------- 主函数 ----------

def run_ingest(filepath: Path) -> None:
    """
    摄入单个文件的完整流程。

    Args:
        filepath: inbox/ 中待处理文件的路径
    """
    filepath = Path(filepath)
    logger.info(f"[Ingest] 开始处理: {filepath.name}")

    # Step 1: 加载文件
    loader = DocumentLoader()
    text = loader.load_text(filepath)
    logger.info(f"[Ingest] 文件加载成功，{len(text)} 字符")

    # Step 2: LLM 知识提取
    logger.info("[Ingest] 调用 LLM 提取知识...")
    extraction = extract_knowledge(text)
    logger.info(
        f"[Ingest] 提取完成 — "
        f"{len(extraction.key_claims)} 条主张，"
        f"{len(extraction.entities)} 个实体，"
        f"{len(extraction.concepts)} 个概念"
    )

    # Step 3: 生成 wiki node
    slug = _slugify(filepath.stem)
    WIKI_NODES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = WIKI_NODES_DIR / f"{slug}.md"
    content = _render_wiki_node(slug, filepath.name, extraction)
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"[Ingest] Wiki node 已生成: {output_path.relative_to(ROOT_DIR)}")

    # Step 4: 归档源文件
    ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)
    archive_dest = ARCHIVED_DIR / filepath.name
    shutil.move(str(filepath), str(archive_dest))
    logger.info(f"[Ingest] 源文件已归档: inbox/archived/{filepath.name}")

    logger.info(f"[Ingest] ✅ 完成: {filepath.name} → {output_path.name}")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="摄入 inbox/ 中的文件到 wiki_nodes/")
    parser.add_argument("filepath", type=Path, help="要摄入的文件路径")
    args = parser.parse_args()

    run_ingest(args.filepath)

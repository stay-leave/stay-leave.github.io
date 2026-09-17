#!/usr/bin/env python3
"""Convert published Reimu article HTML into Markdown posts."""

from __future__ import annotations

from html import unescape
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path("/workspace")
OUT = ROOT / "hugo-src/content/post"

POSTS = [
    {
        "html": ROOT / "post/deepresearch的mcp实践/index.html",
        "out": OUT / "deepresearch的mcp实践.md",
        "title": "Deepresearch的MCP实践",
        "date": "2025-04-06T17:51:29+08:00",
        "categories": ["Agent"],
        "tags": ["DeepResearch", "MCP", "Agent"],
        "cover": "/images/banner.webp",
        "description": "基于 MCP 工具实现 DeepResearch：本地知识库检索、网络检索与客户端循环。",
    },
    {
        "html": ROOT / "post/多模态rag设计及实践/index.html",
        "out": OUT / "多模态rag设计及实践.md",
        "title": "多模态RAG设计及实践",
        "date": "2024-12-18T12:42:51+08:00",
        "categories": ["RAG"],
        "tags": ["RAG", "多模态", "MinerU"],
        "cover": "/b_images/2024_12_18/1.png",
        "description": "面向舆情论文的多模态 RAG：解析、分块、检索、引用与评估。",
    },
    {
        "html": ROOT / "post/rags自动生成测试集/index.html",
        "out": OUT / "rags自动生成测试集.md",
        "title": "Rags自动生成测试集",
        "date": "2024-12-07T21:59:29+08:00",
        "categories": ["RAG"],
        "tags": ["RAG", "Ragas", "评测"],
        "cover": "/b_images/2024_12_7/2.png",
        "description": "用 Ragas 自动生成 RAG 测试集，以及非英语语料与角色定义。",
    },
    {
        "html": ROOT / "post/rag给回复加上引用/index.html",
        "out": OUT / "rag给回复加上引用.md",
        "title": "RAG给回复加上引用",
        "date": "2024-12-06T15:32:45+08:00",
        "categories": ["RAG"],
        "tags": ["RAG", "引用", "LangChain"],
        "cover": "/b_images/2024_12_6/1.png",
        "description": "给 RAG 回复加引用的六种方法：元数据、提示词、函数调用与后处理。",
    },
]

ALT_MAP = {
    "/b_images/2024_12_18/1.png": "论文数据来源分布",
    "/b_images/2024_12_18/2.png": "层级分块结构",
    "/b_images/2024_12_18/3.png": "查询1 知网 RAG 结果",
    "/b_images/2024_12_18/4.png": "查询1 知网原生结果",
    "/b_images/2024_12_18/5.png": "查询1 本项目结果（上）",
    "/b_images/2024_12_18/6.png": "查询1 本项目结果（下）",
    "/b_images/2024_12_18/7.png": "查询2 知网 RAG 结果（上）",
    "/b_images/2024_12_18/8.png": "查询2 知网 RAG 结果（下）",
    "/b_images/2024_12_18/9.png": "查询2 知网原生结果",
    "/b_images/2024_12_18/10.png": "查询2 本项目结果（上）",
    "/b_images/2024_12_18/11.png": "查询2 本项目结果（下）",
    "/b_images/2024_12_18/12.png": "查询3 知网 RAG 结果（上）",
    "/b_images/2024_12_18/13.png": "查询3 知网 RAG 结果（下）",
    "/b_images/2024_12_18/14.png": "查询3 知网原生结果",
    "/b_images/2024_12_18/15.png": "查询3 本项目结果（上）",
    "/b_images/2024_12_18/16.png": "查询3 本项目结果（下）",
    "/b_images/2024_12_18/17.png": "查询4 知网 RAG 结果（上）",
    "/b_images/2024_12_18/18.png": "查询4 知网 RAG 结果（下）",
    "/b_images/2024_12_18/19.png": "查询4 知网原生结果",
    "/b_images/2024_12_18/20.png": "查询4 本项目结果（上）",
    "/b_images/2024_12_18/21.png": "查询4 本项目结果（下）",
    "/b_images/2024_12_7/1.png": "Ragas 知识图谱转换结果",
    "/b_images/2024_12_7/2.png": "Ragas 自动生成的测试集样例",
    "/b_images/2024_12_6/1.png": "直接挂载 chunk 元数据作为引文",
    "/b_images/2024_12_6/2.png": "提示词方法生成的引用效果",
    "/b_images/2024_12_6/3.png": "文档级函数调用引用效果",
    "/b_images/2024_12_6/4.png": "检索到的原始文段",
    "/b_images/2024_12_6/5.png": "片段级引用后的结果",
    "/b_images/2024_12_6/6.png": "生成后处理添加引用效果",
    "/b_images/2024_12_6/7.png": "相似度后挂载引用效果",
}


def yaml_list(items: list[str]) -> str:
    return "\n".join(f"  - {item}" for item in items)


def chroma_text(pre: Tag) -> str:
    lines = []
    for line in pre.select(".line"):
        cl = line.select_one(".cl")
        text = cl.get_text() if cl else line.get_text()
        lines.append(text.rstrip("\n"))
    code = "\n".join(lines).rstrip() + "\n"
    return unescape(code)


def inline(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    name = node.name
    if name == "a":
        href = node.get("href", "")
        text = "".join(inline(c) for c in node.children).strip() or href
        if not href:
            return text
        return f"[{text}]({href})"
    if name == "img":
        src = node.get("src", "")
        alt = node.get("alt", "") or ""
        if alt in {"", "alt text", "1", "2", "3", "4", "5", "6", "7"}:
            alt = ALT_MAP.get(src, alt or "配图")
        return f"![{alt}]({src})"
    if name in {"strong", "b"}:
        return f"**{''.join(inline(c) for c in node.children)}**"
    if name in {"em", "i"}:
        return f"*{''.join(inline(c) for c in node.children)}*"
    if name == "code":
        return f"`{node.get_text()}`"
    if name == "br":
        return "\n"
    return "".join(inline(c) for c in node.children)


def heading_text(tag: Tag) -> str:
    parts = []
    for child in tag.children:
        if isinstance(child, Tag) and child.get("class") and "header-anchor" in child.get("class"):
            continue
        parts.append(inline(child))
    return "".join(parts).strip()


def convert_entry(entry: Tag) -> str:
    chunks: list[str] = []
    for child in entry.children:
        if isinstance(child, NavigableString):
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name
        if name in {"h1", "h2", "h3", "h4"}:
            level = int(name[1])
            chunks.append("#" * level + " " + heading_text(child))
            chunks.append("")
        elif name == "p":
            text = "".join(inline(c) for c in child.children).strip()
            if text:
                chunks.append(text)
                chunks.append("")
        elif name == "blockquote":
            q = child.get_text().strip()
            chunks.append("\n".join(f"> {line}" if line else ">" for line in q.splitlines()))
            chunks.append("")
        elif name == "ul":
            for li in child.find_all("li", recursive=False):
                chunks.append("- " + "".join(inline(c) for c in li.children).strip())
            chunks.append("")
        elif name == "ol":
            for i, li in enumerate(child.find_all("li", recursive=False), 1):
                chunks.append(f"{i}. " + "".join(inline(c) for c in li.children).strip())
            chunks.append("")
        elif name == "div" and child.select_one("pre"):
            pre = child.select_one("pre")
            code = chroma_text(pre)
            lang = "python"
            code_el = pre.select_one("code")
            if code_el:
                classes = code_el.get("class") or []
                for cls in classes:
                    if cls.startswith("language-") and cls != "language-gdscript3":
                        lang = cls.replace("language-", "")
                        break
            chunks.append(f"```{lang}")
            chunks.append(code.rstrip("\n"))
            chunks.append("```")
            chunks.append("")
        elif name == "pre":
            chunks.append("```python")
            chunks.append(chroma_text(child).rstrip("\n"))
            chunks.append("```")
            chunks.append("")
        elif name == "table":
            rows = []
            for tr in child.find_all("tr"):
                cells = [c.get_text().strip() for c in tr.find_all(["th", "td"])]
                rows.append(cells)
            if rows:
                chunks.append("| " + " | ".join(rows[0]) + " |")
                chunks.append("| " + " | ".join("---" for _ in rows[0]) + " |")
                for row in rows[1:]:
                    chunks.append("| " + " | ".join(row) + " |")
                chunks.append("")
        else:
            text = child.get_text("\n", strip=True)
            if text:
                chunks.append(text)
                chunks.append("")
    while chunks and chunks[-1] == "":
        chunks.pop()
    chunks.append("")
    return "\n".join(chunks)


def front_matter(meta: dict) -> str:
    return "\n".join(
        [
            "---",
            f'title: "{meta["title"]}"',
            f'description: "{meta["description"]}"',
            f'date: {meta["date"]}',
            f'lastmod: {meta["date"]}',
            "draft: false",
            f'cover: "{meta["cover"]}"',
            "categories:",
            yaml_list(meta["categories"]),
            "tags:",
            yaml_list(meta["tags"]),
            "---",
            "",
        ]
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for meta in POSTS:
        soup = BeautifulSoup(meta["html"].read_text(encoding="utf-8"), "html.parser")
        entry = soup.select_one(".article-entry")
        if entry is None:
            raise SystemExit(f"missing article-entry in {meta['html']}")
        body = convert_entry(entry)
        meta["out"].write_text(front_matter(meta) + body, encoding="utf-8")
        print("wrote", meta["out"], "chars", meta["out"].stat().st_size)


if __name__ == "__main__":
    main()

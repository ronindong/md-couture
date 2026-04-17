#!/usr/bin/env python3
"""MD → 带样式 HTML 转换器。用法见 ../SKILL.md 或 --help。"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
STYLES_DIR = SKILL_DIR / "styles"

STYLE_PRIORITY = ["tech-dark-sidebar", "clean-minimal", "notion"]


def die(msg: str, code: int = 1) -> None:
    print(f"错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_deps() -> None:
    try:
        import markdown  # noqa: F401
    except ImportError:
        die(
            "缺少依赖 markdown。请运行:\n"
            "    pip3 install markdown pygments\n"
            "（pygments 用于代码高亮，可选但推荐）"
        )


def list_styles() -> list[str]:
    """按 STYLE_PRIORITY 定义的固定顺序返回，未列入的风格按字母序追加在后面。"""
    available = {p.stem for p in STYLES_DIR.glob("*.html")}
    ordered = [s for s in STYLE_PRIORITY if s in available]
    extras = sorted(available - set(ordered))
    return ordered + extras


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = re.sub(r"[\s\u3000]+", "-", text)
    text = re.sub(r"[^\w\-\u4e00-\u9fff]+", "", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "section"


def extract_title_and_body(md_text: str) -> tuple[str, str, str]:
    """返回 (title, subtitle, body_md). 第一个 # H1 作为 title, 紧跟的引用或斜体段作为 subtitle."""
    lines = md_text.splitlines()
    title = ""
    subtitle = ""
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r"^#\s+(.+?)\s*#*\s*$", stripped)
        if m:
            title = m.group(1).strip()
            body_start = i + 1
            for j in range(i + 1, min(i + 6, len(lines))):
                s = lines[j].strip()
                if not s:
                    continue
                if s.startswith("> "):
                    subtitle = s[2:].strip()
                    body_start = j + 1
                elif s.startswith("*") and s.endswith("*") and not s.startswith("**"):
                    subtitle = s.strip("*").strip()
                    body_start = j + 1
                break
        break
    body = "\n".join(lines[body_start:]) if title else md_text
    return title, subtitle, body


class SlugTreeprocessor:
    """为所有 heading 注入稳定 id，同时收集 TOC 条目。"""

    def __init__(self):
        self.headings: list[tuple[int, str, str]] = []
        self._used: set[str] = set()

    def __call__(self, tree):
        from xml.etree.ElementTree import tostring

        for el in tree.iter():
            tag = el.tag.lower() if isinstance(el.tag, str) else ""
            if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                level = int(tag[1])
                text = "".join(el.itertext()).strip()
                if not text:
                    continue
                base = slugify(text)
                sid = base
                n = 2
                while sid in self._used:
                    sid = f"{base}-{n}"
                    n += 1
                self._used.add(sid)
                el.set("id", sid)
                self.headings.append((level, sid, text))
        return tree


def render_markdown(md_body: str) -> tuple[str, list[tuple[int, str, str]]]:
    import markdown
    from markdown.treeprocessors import Treeprocessor
    from markdown.extensions import Extension

    collector = SlugTreeprocessor()

    class _TP(Treeprocessor):
        def run(self, root):
            return collector(root)

    class _Ext(Extension):
        def extendMarkdown(self, md):
            md.treeprocessors.register(_TP(md), "slug_collect", 5)

    md = markdown.Markdown(
        extensions=[
            "extra",
            "sane_lists",
            "tables",
            "fenced_code",
            "codehilite",
            _Ext(),
        ],
        extension_configs={
            "codehilite": {"guess_lang": False, "noclasses": True},
        },
        output_format="html5",
    )
    html = md.convert(md_body)
    return html, collector.headings


def build_sidebar_toc(headings: list[tuple[int, str, str]]) -> str:
    if not headings:
        return "<!-- no headings -->"
    top_items = [h for h in headings if h[0] == 2]
    use_level = 2 if top_items else min(h[0] for h in headings)
    out: list[str] = []
    n = 0
    for level, sid, text in headings:
        if level == use_level:
            n += 1
            out.append(
                f'<a href="#{sid}" class="lvl-1"><span class="num">{n}.</span>{text}</a>'
            )
        elif level == use_level + 1:
            out.append(f'<a href="#{sid}" class="lvl-2">{text}</a>')
        elif level == use_level + 2:
            out.append(f'<a href="#{sid}" class="lvl-3">{text}</a>')
    return "\n    ".join(out)


def build_block_toc(headings: list[tuple[int, str, str]]) -> str:
    if not headings:
        return ""
    top_items = [h for h in headings if h[0] == 2]
    use_level = 2 if top_items else min(h[0] for h in headings)
    lines = ['<div class="toc">', '  <div class="toc-title">目录 · Contents</div>', "  <ul>"]
    open_levels = [use_level]
    first = True
    for level, sid, text in headings:
        if level < use_level or level > use_level + 2:
            continue
        while open_levels and level < open_levels[-1]:
            lines.append("    " + "  " * (len(open_levels) - 1) + "</li></ul>")
            open_levels.pop()
        if level > open_levels[-1]:
            lines.append("    " + "  " * len(open_levels) + "<ul>")
            open_levels.append(level)
        else:
            if not first:
                lines.append("    " + "  " * (len(open_levels) - 1) + "</li>")
        indent = "    " + "  " * (len(open_levels) - 1)
        lines.append(f'{indent}<li><a href="#{sid}">{text}</a>')
        first = False
    while len(open_levels) > 1:
        lines.append("    " + "  " * (len(open_levels) - 1) + "</li></ul>")
        open_levels.pop()
    lines.append("    </li>")
    lines.append("  </ul>")
    lines.append("</div>")
    return "\n".join(lines)


def render(md_path: Path, style: str, title_override: str | None = None) -> str:
    tpl_path = STYLES_DIR / f"{style}.html"
    if not tpl_path.exists():
        die(f"风格 '{style}' 不存在。可用: {', '.join(list_styles())}")
    template = tpl_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")

    title, subtitle, body = extract_title_and_body(md_text)
    if title_override:
        title = title_override
    if not title:
        title = md_path.stem

    content_html, headings = render_markdown(body)
    sidebar_toc = build_sidebar_toc(headings)
    block_toc = build_block_toc(headings)

    return (
        template.replace("{{TITLE}}", title)
        .replace("{{SUBTITLE}}", subtitle)
        .replace("{{TOC}}", sidebar_toc)
        .replace("{{TOC_BLOCK}}", block_toc)
        .replace("{{CONTENT}}", content_html)
    )


def main() -> None:
    ensure_deps()
    ap = argparse.ArgumentParser(description="MD → 带样式 HTML")
    ap.add_argument("input", help="输入 .md 文件路径")
    ap.add_argument(
        "--style", "-s", default="tech-dark-sidebar",
        help=f"样式 id（默认 tech-dark-sidebar）。可用: {', '.join(list_styles())}",
    )
    ap.add_argument("--output", "-o", help="输出 .html 路径（默认同目录同名）")
    ap.add_argument("--title", help="覆盖文档标题")
    args = ap.parse_args()

    md_path = Path(args.input).expanduser().resolve()
    if not md_path.exists():
        die(f"找不到文件: {md_path}")

    out_path = Path(args.output).expanduser().resolve() if args.output else md_path.with_suffix(".html")
    html = render(md_path, args.style, args.title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"✓ 已生成: {out_path}")
    print(f"  风格: {args.style}")
    print(f"  来源: {md_path}")


if __name__ == "__main__":
    main()

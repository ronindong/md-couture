#!/usr/bin/env python3
"""为给定 md 文件在 3 种风格下各生成一个 demo，并输出一个可交互的风格选择页 index.html。

额外: 若本机可找到 headless Chrome/Chromium/Edge，会为每种风格截一张 PNG
(thumb-<id>.png)，方便在 Cursor 聊天里直接贴图预览。

预览产物默认放到 skill 的 .cache 目录（~/.cursor/skills/md-couture/.cache/），
不污染用户工作区；每次运行会清理超过 CACHE_TTL_DAYS 天未访问的旧缓存。"""
from __future__ import annotations

import argparse
import hashlib
import html as html_mod
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CACHE_DIR = SKILL_DIR / ".cache"
CACHE_TTL_DAYS = 7

sys.path.insert(0, str(SCRIPT_DIR))

from convert import ensure_deps, list_styles, render  # noqa: E402


def cache_dir_for(md_path: Path) -> Path:
    """为给定 md 生成稳定的缓存子目录路径（基于绝对路径 hash + 文件名）。"""
    digest = hashlib.sha1(str(md_path).encode("utf-8")).hexdigest()[:10]
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in md_path.stem)[:40]
    return CACHE_DIR / f"{digest}-{safe_stem}"


def sweep_cache(ttl_days: int = CACHE_TTL_DAYS) -> int:
    """删除 .cache 下 mtime 早于 ttl_days 的子目录，返回清理数量。"""
    if not CACHE_DIR.exists():
        return 0
    cutoff = time.time() - ttl_days * 86400
    removed = 0
    for sub in CACHE_DIR.iterdir():
        if not sub.is_dir():
            continue
        try:
            latest = max((p.stat().st_mtime for p in sub.rglob("*")), default=sub.stat().st_mtime)
            if latest < cutoff:
                shutil.rmtree(sub, ignore_errors=True)
                removed += 1
        except Exception:
            continue
    return removed


STYLE_META: dict[str, dict[str, str]] = {
    "tech-dark-sidebar": {
        "name": "Tech Dark Sidebar",
        "tagline": "深色侧栏 · 红色高亮 · 卡片内容",
        "use": "技术文档、方法论、长文导读",
        "gradient": "linear-gradient(135deg,#1a1a2e 0%,#16213e 60%,#e94560 120%)",
        "fg": "#fff",
    },
    "clean-minimal": {
        "name": "Clean Minimal",
        "tagline": "GitHub 风 · 白底窄栏 · 克制",
        "use": "README、说明文档、博客",
        "gradient": "linear-gradient(135deg,#ffffff 0%,#f6f8fa 60%,#d0d7de 120%)",
        "fg": "#1f2328",
    },
    "notion": {
        "name": "Notion Style",
        "tagline": "暖色调 · 柔和阴影 · 精致排版",
        "use": "笔记、随笔、知识整理",
        "gradient": "linear-gradient(135deg,#fbfaf7 0%,#efe4d6 60%,#d7c1a4 120%)",
        "fg": "#37352f",
    },
}


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>选择风格 · {title}</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
       background:#0f0f14;color:#e4e4ea;min-height:100vh;padding:48px 24px 80px;line-height:1.6}}
  .wrap{{max-width:1180px;margin:0 auto}}
  header{{text-align:center;margin-bottom:48px}}
  header h1{{font-size:2rem;font-weight:800;margin-bottom:8px}}
  header .src{{color:#8a8a98;font-size:.9rem;font-family:"SF Mono",Menlo,monospace}}
  header .tip{{margin-top:18px;display:inline-block;padding:10px 20px;background:#1a1a2e;border:1px solid #2a2a44;
              border-radius:8px;color:#c5c5d1;font-size:.9rem}}
  header .tip b{{color:#e94560}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}}
  .card{{background:#16161f;border:1px solid #2a2a3a;border-radius:12px;overflow:hidden;
         transition:transform .2s,border-color .2s,box-shadow .2s;display:flex;flex-direction:column}}
  .card:hover{{transform:translateY(-4px);border-color:#e94560;box-shadow:0 12px 40px rgba(233,69,96,.15)}}
  .thumb{{height:180px;position:relative;overflow:hidden;display:flex;align-items:flex-end;padding:18px 22px}}
  .thumb .big{{font-size:1.4rem;font-weight:800}}
  .thumb .small{{font-size:.8rem;opacity:.85;margin-top:4px}}
  .thumb-sidebar{{position:absolute;left:0;top:0;bottom:0;width:30%;background:rgba(0,0,0,.35)}}
  .thumb-lines{{position:absolute;right:18px;top:22px;bottom:44px;left:35%}}
  .thumb-lines::before,.thumb-lines::after{{content:"";position:absolute;left:0;right:0;height:4px;background:currentColor;opacity:.35;border-radius:2px}}
  .thumb-lines::before{{top:0;width:70%}}
  .thumb-lines::after{{top:14px;width:90%}}
  .body{{padding:20px 22px 22px;flex:1;display:flex;flex-direction:column}}
  .body h3{{font-size:1.05rem;margin-bottom:6px;color:#fff}}
  .body .tag{{color:#8a8a98;font-size:.82rem;margin-bottom:14px}}
  .body .use{{color:#c5c5d1;font-size:.88rem;margin-bottom:18px}}
  .body .id{{font-family:"SF Mono",Menlo,monospace;font-size:.78rem;color:#e94560;margin-bottom:18px}}
  .actions{{margin-top:auto;display:flex;gap:8px}}
  .btn{{flex:1;padding:10px 14px;border:1px solid #2a2a3a;background:transparent;color:#e4e4ea;
        border-radius:6px;cursor:pointer;font-size:.88rem;text-decoration:none;text-align:center;
        transition:background .15s,border-color .15s}}
  .btn:hover{{background:#1e1e2e;border-color:#555}}
  .btn.primary{{background:#e94560;border-color:#e94560;color:#fff;font-weight:600}}
  .btn.primary:hover{{background:#d8334e;border-color:#d8334e}}
  footer{{margin-top:48px;text-align:center;color:#666;font-size:.82rem}}
  footer code{{background:#1a1a2e;padding:2px 8px;border-radius:4px;color:#c5c5d1;font-size:.9em}}
</style></head><body>
<div class="wrap">
<header>
  <h1>选择一个风格</h1>
  <div class="src">源: {src}</div>
  <div class="tip">点卡片上的 <b>完整预览</b> 在浏览器里查看效果 · 选定后告诉 AI 你要的 <b>风格 id</b></div>
</header>
<div class="grid">
{cards}
</div>
<footer>
  生成最终文件: <code>python3 convert.py {src_basename} --style &lt;id&gt;</code>
</footer>
</div></body></html>
"""


def find_chrome() -> str | None:
    """返回可用的 headless 浏览器可执行路径，找不到返回 None。"""
    candidates: list[str] = []
    if sys.platform == "darwin":
        candidates += [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Arc.app/Contents/MacOS/Arc",
        ]
    candidates += ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge"]
    for c in candidates:
        if "/" in c and Path(c).exists():
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def screenshot_demos(out_dir: Path, style_ids: list[str], width: int = 1400, height: int = 900) -> list[Path]:
    """为每个 demo html 在 out_dir 里截图为 thumb-<id>.png。返回成功生成的路径列表。"""
    chrome = find_chrome()
    if not chrome:
        print("ℹ 未找到 Chrome/Chromium，跳过 PNG 截图生成（预览页仍可用）", file=sys.stderr)
        return []
    pngs: list[Path] = []
    for sid in style_ids:
        demo = out_dir / f"{sid}.html"
        png = out_dir / f"thumb-{sid}.png"
        if not demo.exists():
            continue
        try:
            subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--no-sandbox",
                    f"--window-size={width},{height}",
                    f"--screenshot={png}",
                    f"file://{demo}",
                ],
                check=False,
                capture_output=True,
                timeout=30,
            )
            if png.exists() and png.stat().st_size > 0:
                pngs.append(png)
        except Exception as e:
            print(f"  ! 截图失败 {sid}: {e}", file=sys.stderr)
    return pngs


CARD_TEMPLATE = """<div class="card">
  <div class="thumb" style="background:{gradient};color:{fg}">
    <div class="thumb-sidebar"></div>
    <div class="thumb-lines"></div>
    <div>
      <div class="big">{name}</div>
      <div class="small">{tagline}</div>
    </div>
  </div>
  <div class="body">
    <h3>{name}</h3>
    <div class="id">id: {sid}</div>
    <div class="use">适合: {use}</div>
    <div class="actions">
      <a class="btn primary" href="{demo}" target="_blank" rel="noopener">完整预览 →</a>
    </div>
  </div>
</div>"""


def main() -> None:
    ensure_deps()
    ap = argparse.ArgumentParser(description="生成多风格预览选择页")
    ap.add_argument("input", help="输入 .md 文件路径")
    ap.add_argument("--out-dir", help="输出目录（默认放在 skill 的 .cache 中，不污染用户工作区）")
    ap.add_argument("--no-screenshots", action="store_true", help="跳过 PNG 截图生成")
    ap.add_argument("--no-sweep", action="store_true", help="跳过过期缓存清理")
    args = ap.parse_args()

    md_path = Path(args.input).expanduser().resolve()
    if not md_path.exists():
        print(f"错误: 找不到文件 {md_path}", file=sys.stderr)
        sys.exit(1)

    if not args.no_sweep:
        swept = sweep_cache()
        if swept:
            print(f"🧹 清理了 {swept} 个过期缓存（>{CACHE_TTL_DAYS} 天未访问）")

    if args.out_dir:
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_dir = cache_dir_for(md_path)
    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    available = list_styles()
    cards = []
    for sid in available:
        meta = STYLE_META.get(sid, {
            "name": sid, "tagline": "自定义风格", "use": "—",
            "gradient": "linear-gradient(135deg,#444,#222)", "fg": "#fff",
        })
        demo_path = out_dir / f"{sid}.html"
        demo_path.write_text(render(md_path, sid), encoding="utf-8")
        cards.append(CARD_TEMPLATE.format(
            sid=sid,
            name=html_mod.escape(meta["name"]),
            tagline=html_mod.escape(meta["tagline"]),
            use=html_mod.escape(meta["use"]),
            gradient=meta["gradient"],
            fg=meta["fg"],
            demo=f"{sid}.html",
        ))

    index_html = INDEX_TEMPLATE.format(
        title=html_mod.escape(md_path.stem),
        src=html_mod.escape(str(md_path)),
        src_basename=html_mod.escape(md_path.name),
        cards="\n".join(cards),
    )
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")

    print(f"✓ 预览已生成: {out_dir}")
    print(f"  打开: {out_dir / 'index.html'}")
    print(f"  可选风格: {', '.join(available)}")

    if not args.no_screenshots:
        pngs = screenshot_demos(out_dir, available)
        if pngs:
            print("✓ 已生成风格缩略图（AI 可直接在对话里贴图预览）:")
            for p in pngs:
                print(f"  - {p}")


if __name__ == "__main__":
    main()

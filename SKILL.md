---
name: md-couture
description: 把 Markdown 文件转换成带精美样式的单文件 HTML（md-couture），支持多种主题（Tech Dark Sidebar、Clean Minimal、Notion Style）可选。当用户说"md 转 html""转 html""markdown 转 html""美化文档""把文档导出成 html""生成带样式的 html""文档网页化"等时使用此技能。
---

# MD → Styled HTML 转换器

把 `.md` 文件转换成**带精美样式、自包含的单文件 HTML**。内置 3 种主题，支持预览选择。

## 可用主题（展示顺序固定，默认主题 = 第一个）

| # | id | 名称 | 特点 | 适合场景 |
|---|----|------|------|---------|
| ① | `tech-dark-sidebar` | Tech Dark Sidebar | 深色导航侧栏 + 红色高亮 + 卡片式内容 | 技术文档、方法论、长文导读 |
| ② | `clean-minimal` | Clean Minimal | GitHub 风、白底、窄栏、克制 | README、说明文档、博客 |
| ③ | `notion` | Notion Style | 暖色调、柔和阴影、无边框 | 笔记、随笔、知识整理 |

**重要**：预览时必须按上述顺序呈现 ①→②→③，`tech-dark-sidebar` 固定排第一位。
这个顺序由 `convert.py::STYLE_PRIORITY` 统一定义，想调整优先级只需改那个列表。

---

## 触发场景 → 直接执行

当用户的请求匹配以下任一模式，**直接进入对应流程**，不要反复确认：

| 用户说法 | 怎么做 |
|---------|-------|
| "把 X.md 转成 html"（未指定风格） | 先跑**预览流程**让用户选风格 |
| "用 tech-dark / notion / clean 风格转 X.md" | 直接跑**转换流程** |
| "我要之前那个风格 / 深色侧栏那个" | 直接用 `tech-dark-sidebar` |
| "美化这个 md / 文档网页化" | 默认先预览 |
| "看看有哪些风格 / 预览" | 只跑**预览流程** |

---

## 流程 A：转换（已知风格）

```bash
python3 ~/.cursor/skills/md-couture/scripts/convert.py \
  <输入.md> \
  --style <tech-dark-sidebar|clean-minimal|notion> \
  [--output <输出.html>] \
  [--title "自定义标题"]
```

默认 `--output` 与输入同目录、同名、`.html` 后缀。

**执行步骤**：

1. 用 `Shell` 工具跑上面的命令
2. 脚本输出成功路径后，用一句话告诉用户 "已生成 `<path>`，用浏览器打开即可"
3. **不要**把 HTML 源码贴回对话里（文件已经生成）

---

## 流程 B：预览选择（未知风格）

需要让用户看到 3 种风格的实际效果再选。**优先在 Cursor 聊天里贴 PNG 给用户看**，而不是让用户开浏览器。

```bash
python3 ~/.cursor/skills/md-couture/scripts/preview.py <输入.md>
```

脚本会在 **skill 的缓存目录**（不污染用户工作区）生成：

```
~/.cursor/skills/md-couture/.cache/<hash>-<md名>/
├── index.html               # 风格选择网格页（备用，浏览器打开用）
├── <style>.html × N         # 每种风格的完整 demo
└── thumb-<style>.png × N    # 每种风格的首屏截图（给 AI 贴图用）
```

- `<hash>` = md 绝对路径的 sha1 前 10 位（同一文件每次路径稳定，会覆盖旧缓存）
- 每次运行会清理 `.cache` 下 **> 7 天未访问** 的其他子目录
- 脚本会打印 `thumb-*.png` 的完整路径，AI **直接从输出里取路径并 Read**

**AI 必须严格按以下模板输出**（顺序不可乱、三个元素都不能省）：

对每一种风格，按下面的结构生成一个 block：

```
### ① <风格 id> — <一句话特点>

[用 Read 工具读取 thumb-<风格id>.png ← 这一步让图片渲染进对话]

📂 `<thumb PNG 的绝对路径>`
```

第三行的**绝对路径用反引号包住**—— Cursor 会把它变成可 cmd+click 打开的文件链接，
这样用户既能在对话里看缩略图，也能点击路径用系统图片查看器放大细看。

全部三种风格都贴完后，结尾一句：

> 告诉我选哪个（如 "tech-dark" / "第一个" / "notion"），我就生成正式文件。

**绝对不要**只输出文字描述而不贴图/不给路径 —— 这是这个 skill 存在的唯一意义。
**绝对不要**让用户"在浏览器里打开 index.html"—— 违背设计意图。
只有在脚本输出显示"未找到 Chrome"时，才退回到让用户开 index.html。

用户选定后，跑流程 A 生成最终文件（默认输出到原 md 同目录、同名 `.html`）。缓存无需手动清理，skill 自动管理。

---

## 依赖

脚本使用 Python 3 + `markdown` 包。如未安装：

```bash
pip3 install markdown pygments
```

脚本内部已做了依赖检查，未安装会提示一次安装命令，不要多次重复。

---

## 可扩展

想加新风格：在 `styles/` 下新增 `<id>.html` 模板文件，包含以下占位符即可被脚本识别：

- `{{TITLE}}` — 文档标题（取 md 的第一个 `# H1`，没有就用文件名）
- `{{SUBTITLE}}` — 可选副标题（空字符串 OK）
- `{{TOC}}` — 自动生成的目录 HTML（侧栏用）
- `{{CONTENT}}` — 转换后的主体 HTML

新风格自动出现在 `preview.py` 的预览页里，无需改代码。

---

## 约束

- **单文件自包含**：所有 CSS 内联到 `<style>`，不依赖外部 CDN
- **响应式**：移动端必须可读（模板里已写了 media query）
- **不要改 md 内容**：只做渲染，不总结不改写
- **中文优先**：字体栈含 PingFang SC / Microsoft YaHei

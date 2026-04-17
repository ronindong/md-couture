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
| "把 X.md 转成 html"（未指定风格） | 走**流程 B · 快速模式**（给固定样例图路径，不 Read） |
| "用 tech-dark / notion / clean 风格转 X.md" | 直接走**流程 A** |
| "我要之前那个风格 / 深色侧栏那个" | 直接用 `tech-dark-sidebar` |
| "美化这个 md / 文档网页化" | 走**流程 B · 快速模式** |
| "看看有哪些风格 / 预览" | 走**流程 B · 快速模式** |
| "用我的文档预览 / 看我这篇长啥样 / 真实预览" | 走**流程 B · 真实模式**（跑 preview.py） |

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

**两种模式**，默认走**快速模式**（极省 token）。

---

### 流程 B1 · 快速模式（默认，~500 token）

**不跑任何脚本，不 Read 任何图片**。直接引用 skill 自带的 3 张固定样例截图路径（基于通用 `demo.md` 渲染）。

这 3 张图在仓库里固定存在：

```
~/.cursor/skills/md-couture/assets/screenshots/thumb-tech-dark-sidebar.png
~/.cursor/skills/md-couture/assets/screenshots/thumb-clean-minimal.png
~/.cursor/skills/md-couture/assets/screenshots/thumb-notion.png
```

**AI 必须严格按以下模板输出**（不要加别的，不要 Read）：

```markdown
3 种主题预览（点下方路径 cmd+click 打开放大看）：

### ① `tech-dark-sidebar` — 深色导航侧栏 + 红色高亮 + 卡片式内容
📂 `/Users/<USER>/.cursor/skills/md-couture/assets/screenshots/thumb-tech-dark-sidebar.png`
**适合**：技术文档、方法论、长文导读

### ② `clean-minimal` — GitHub 风，白底、窄栏、克制
📂 `/Users/<USER>/.cursor/skills/md-couture/assets/screenshots/thumb-clean-minimal.png`
**适合**：README、说明文档、博客

### ③ `notion` — 暖色调、柔和阴影、封面条
📂 `/Users/<USER>/.cursor/skills/md-couture/assets/screenshots/thumb-notion.png`
**适合**：笔记、随笔、知识整理

---
选哪个？告诉我 `tech-dark` / `clean` / `notion`，或 `第一个` / `第二个` / `第三个` 即可。
如果想看**用你自己文档内容**渲染的真实预览，说一声"用我文档预览"。
```

**关键规则**：
- 路径**一定用反引号包起来**（Cursor 会变成 cmd+click 可点文件链接）
- 路径里的 `<USER>` 要替换成真实用户名（从 `~` 展开或 `$HOME` 取）
- **绝对不要 Read 这 3 张图**（这是快速模式的全部意义，Read 就会多花 ~5K token）
- 不要跑 `preview.py`（除非用户明确要求真实预览）

---

### 流程 B2 · 真实模式（用户明确要求时才走，~5-10K token）

触发条件：用户说"用我文档预览"、"看我这篇长啥样"、"真实渲染看看"、"用我内容渲染出来看看" 等。

```bash
python3 ~/.cursor/skills/md-couture/scripts/preview.py <输入.md>
```

脚本会在 `~/.cursor/skills/md-couture/.cache/<hash>-<md名>/` 下生成 demo HTML 和 per-doc 截图，每次运行会清理 7 天以上未访问的旧缓存。

真实模式下，AI 才 Read 生成的 `thumb-*.png` 并贴进对话，让用户看到自己文档的实际渲染效果。输出格式同快速模式，只是路径改成缓存目录里的。

---

用户选定风格后，一律跑流程 A 生成最终 HTML。缓存和样例截图都不用手动管理。

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

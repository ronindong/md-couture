# md-couture 示例文档

> 这是一份用来展示 md-couture 转换效果的样例文档，覆盖了标题、表格、代码、列表、引用、链接等常见 Markdown 元素。

## 项目简介

md-couture 是一个把 **Markdown** 转换成**带精美样式的单文件 HTML** 的小工具。原生支持 3 种主题：Tech Dark Sidebar、Clean Minimal、Notion Style，开箱即用。

核心设计：

- **单文件自包含** — CSS 全内联，不依赖 CDN
- **自动目录** — 从 `##` 抽取，生成可导航侧栏/内嵌目录
- **Cursor Skill 集成** — 对话里直接出图预览、选主题
- **可扩展** — 丢一个模板就是一种新主题

## 快速上手

### 安装依赖

```bash
pip3 install --user markdown pygments
```

### 命令行转换

```bash
python3 scripts/convert.py examples/demo.md --style tech-dark-sidebar
```

### 多主题预览

```bash
python3 scripts/preview.py examples/demo.md
```

## 主题对比

| # | 主题 ID | 风格关键词 | 适合场景 |
|---|---------|-----------|---------|
| ① | `tech-dark-sidebar` | 深色侧栏、红色高亮、卡片式 | 技术文档、长文导读 |
| ② | `clean-minimal` | GitHub 风、白底、窄栏 | README、说明文档 |
| ③ | `notion` | 暖色调、封面条、柔和排版 | 笔记、随笔、知识整理 |

## 设计哲学

1. **默认即美**：用户什么都不配置，第一次转换就能拿出得体的成品
2. **零污染**：中间产物全部放进 skill 的 `.cache/`，不在用户工作区留垃圾
3. **对话友好**：AI 能直接在 Cursor 聊天里贴出 PNG 预览，不用开浏览器

## 致谢

- 字体栈借鉴了 [GitHub Primer](https://primer.style/)
- 代码高亮基于 [Pygments](https://pygments.org/)
- 主题灵感来自 Notion、Linear、Stripe Docs

---

*Powered by md-couture — stylish markdown, zero config.*

# 我给 Cursor 做了个 Skill，让它一句话把 Markdown 转成好看的 HTML

> **TL;DR** — 开源了个小工具 [md-couture](https://github.com/ronindong/md-couture)，3 种内置主题，在 Cursor 里对 AI 说一句"转 html"就能出成品。纯 Python + 原生 CSS，转换本身 0 token。

## 起因：我被自己的 Markdown 烦到了

写了几年 md 笔记，每次想分享给别人时总是要经历：

- 直接发 `.md`？对方没装 markdown 阅读器
- 发 GitHub renderer 链接？有些笔记不适合进仓库
- 用 Typora 导出？样式固定、装软件、还要额外操作
- 让 AI 当场生成带样式的 HTML？**每次都在烧 token**，而且每次样式还都不一样

核心需求其实很简单：

> **给我 3 种看着舒服的模板，我丢个 `.md` 进去，出来一个能直接分享的 HTML 就行。**

## 成品长这样

**① Tech Dark Sidebar** — 深色侧栏 + 红色高亮 + 卡片式内容，适合技术长文

![tech-dark-sidebar](https://raw.githubusercontent.com/ronindong/md-couture/main/assets/screenshots/thumb-tech-dark-sidebar.png)

**② Clean Minimal** — GitHub 风，白底窄栏，克制

![clean-minimal](https://raw.githubusercontent.com/ronindong/md-couture/main/assets/screenshots/thumb-clean-minimal.png)

**③ Notion Style** — 暖色调、封面条、柔和排版

![notion](https://raw.githubusercontent.com/ronindong/md-couture/main/assets/screenshots/thumb-notion.png)

## 30 秒上手

```bash
git clone https://github.com/ronindong/md-couture.git ~/.cursor/skills/md-couture
pip3 install --user markdown pygments
```

然后在 Cursor 里打开任何一个 `.md` 文件，对 AI 说：

> "把这个转成 html"

AI 会把 3 种风格的预览路径贴回对话（cmd+click 直接看大图），你选一个，它就在 md 同目录输出 `.html`。一句话搞定。

如果风格已经确定，直接指定就行：

> "用 notion 风格转这个"

## 我觉得最巧妙的两点

### 1. 0 token 转换

很多人用 AI 做文档美化就是让 AI 当场写 HTML。这路子我一开始也走过，**单次耗 20K+ token，每次样式还不一样**。

这个 skill 的做法：

- **AI 只负责理解触发词 + 调用脚本**（~500 token）
- **实际的 MD 解析、HTML 生成全是本地 Python**（0 token）
- 你转 100 个文件，AI 消耗几乎不变

换句话说：一次性产出可复用的模板和脚本，比让 AI 每次重复劳动划算得多。这也算是 Agentic Skill 的精髓。

### 2. 双模式预览：快/真按需切换

Cursor 对话里渲染一张 1400×900 的 PNG 大约要消耗 **1.5K image token**。预览 3 张就是 5K+。

我用了两种模式：

| 场景 | 模式 | AI 消耗 |
|---|---|---|
| 你只是想挑个风格 | **快速模式** — 只返回 3 张**固定样例图路径**让你自己 cmd+click 打开 | **~500 token** |
| 你想看自己文档真实渲染效果 | **真实模式** — 跑 headless Chrome 实际截图 + Read 进对话 | ~5–10K token |

触发词很自然：

- "转 html" → 快速模式（默认）
- "用我的文档预览看看" → 真实模式（明确要真实效果）

这种**让用户为知情付费** 的设计，比一刀切地总是烧 token 舒服多了。

### 3. 零工作区污染

中间产物（per-doc 截图、临时 HTML）全部放在 skill 自己的 `.cache/` 里，基于 `sha1(md路径)[:10]` 命名子目录，**7 天没访问自动清理**。用户 workspace 永远干净。

## 架构

```
md-couture/
├── SKILL.md              # 给 Cursor AI 的指令文档
├── scripts/
│   ├── convert.py        # MD → HTML 主转换器
│   └── preview.py        # 多主题预览 + 截图管线
├── styles/
│   ├── tech-dark-sidebar.html
│   ├── clean-minimal.html
│   └── notion.html
├── examples/demo.md      # 演示文档
└── assets/screenshots/   # 3 张固定样例图（快速模式用）
```

扩展成本极低：

> 想加新主题？在 `styles/` 里丢一个带 `{{TITLE}} {{TOC}} {{CONTENT}}` 占位符的 HTML 就行，`preview.py` 自动识别。

## 一些延伸思考

做这个小工具过程中复读了一遍 Cursor Agent Skill 的文档，感触比较深的几点：

1. **Skill 不是"让 AI 做事"，而是"告诉 AI 什么时候走脚本"**。核心价值在用自然语言触发确定性执行。
2. **能用脚本就别让模型生成**。脚本一次写好，每次跑结果一致；模型每次推理都在消耗 token 还可能出错。
3. **触发词要写得足够"口语化"**。别只写"convert markdown to html"，用户真实表达是"美化这个文档"、"转 html"、"给我弄好看点"。SKILL.md 的描述字段是 AI 判断触发的核心。

## 仓库

👉 https://github.com/ronindong/md-couture

欢迎 Star / Issue / PR。特别欢迎有人贡献新主题（比如学术论文风、杂志风、暗黑终端风），加一个新样式只需要写一个 HTML 模板文件。

---

> 如果你也在用 Cursor 又经常写 markdown，这个 skill 可能能帮到你。装好以后基本是我 IDE 里用得最频繁的 skill 之一。

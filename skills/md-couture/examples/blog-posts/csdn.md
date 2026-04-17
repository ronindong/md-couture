# Cursor 插件分享 | md-couture：一键将 Markdown 转换成带精美样式的 HTML（附完整源码）

> **关键词**：Cursor、Cursor Skill、Markdown 转 HTML、Agentic Skill、文档美化、Python、开源工具  
> **GitHub**：https://github.com/ronindong/md-couture  
> **适用人群**：经常写 Markdown 文档、在 Cursor 中进行 AI 辅助开发的开发者

## 前言

作为一个经常写技术文档的开发者，我每天都会产出大量的 Markdown 文件。但在分享给非技术人员或需要作为正式文档输出时，原生 `.md` 文件的可读性和美观度都不够理想。

本文将分享我基于 Cursor Skill 能力自研的一款开源小工具 **md-couture**，它可以让你在 Cursor 中对 AI 说一句 "把这个转成 HTML"，就能得到一份带精美样式、自包含的单文件 HTML 文档。

## 一、项目简介

md-couture 是一款基于 Cursor Agent Skill 体系开发的 Markdown 美化工具，核心功能如下：

- **3 种内置主题**：Tech Dark Sidebar（深色侧栏）/ Clean Minimal（GitHub 风）/ Notion Style（暖色调）
- **单文件自包含**：输出的 HTML 将所有 CSS 内联，不依赖任何外部 CDN 或资源
- **自动目录生成**：基于 H2/H3 标题自动生成可导航侧栏或内嵌 TOC，支持中文 slug
- **Cursor 对话式操作**：通过 AI 在聊天中预览、选择主题并触发生成
- **零工作区污染**：所有中间产物缓存在 skill 目录，7 天自动清理
- **完全开源**：MIT 协议，可自由使用、修改、分发

## 二、效果预览

### 2.1 主题一：Tech Dark Sidebar

深色导航侧栏配合红色高亮，卡片式内容布局，适合技术文档、方法论类长文。

![tech-dark-sidebar](https://raw.githubusercontent.com/ronindong/md-couture/main/assets/screenshots/thumb-tech-dark-sidebar.png)

### 2.2 主题二：Clean Minimal

GitHub 风格，白色底色、窄栏居中、排版克制，适合 README、产品说明等简洁场景。

![clean-minimal](https://raw.githubusercontent.com/ronindong/md-couture/main/assets/screenshots/thumb-clean-minimal.png)

### 2.3 主题三：Notion Style

暖色调封面 + 柔和阴影 + 无边框列表，适合笔记整理、随笔、知识库类文档。

![notion](https://raw.githubusercontent.com/ronindong/md-couture/main/assets/screenshots/thumb-notion.png)

## 三、安装与使用

### 3.1 前置要求

- **Python 3.9+**
- **Cursor IDE**（作为 Skill 使用时）
- **macOS / Linux / Windows**（跨平台）
- **Google Chrome**（可选，用于生成预览截图）

### 3.2 安装步骤

**方式 A：作为 Cursor Skill 使用（推荐）**

```bash
git clone https://github.com/ronindong/md-couture.git ~/.cursor/skills/md-couture
pip3 install --user markdown pygments
```

安装完成后重启 Cursor，即可通过自然语言触发。

**方式 B：作为独立 CLI 工具使用**

```bash
git clone https://github.com/ronindong/md-couture.git
cd md-couture
pip3 install --user markdown pygments
python3 scripts/convert.py examples/demo.md --style tech-dark-sidebar
```

### 3.3 在 Cursor 中使用

安装完成后，打开任意 `.md` 文件，对 AI 说：

**场景 1：不确定风格，先预览**

```
把这个文档转成 html
```

AI 会返回 3 种主题的预览路径，点击路径 cmd+click 即可打开放大查看。选定后告诉 AI 即可生成。

**场景 2：已明确风格**

```
用 notion 风格转这个文档
```

或：

```
用深色侧栏那个风格
```

AI 会直接调用脚本生成 HTML，输出到原 MD 同目录。

### 3.4 命令行使用

```bash
# 最简用法
python3 scripts/convert.py 文档.md --style tech-dark-sidebar

# 指定输出路径和自定义标题
python3 scripts/convert.py 文档.md \
    --style notion \
    --output ~/Desktop/文档.html \
    --title "我的文档"

# 生成所有主题的预览
python3 scripts/preview.py 文档.md
```

## 四、技术实现要点

### 4.1 核心架构

```
md-couture/
├── SKILL.md                  # Cursor Skill 指令文件
├── scripts/
│   ├── convert.py            # 主转换器（Markdown → HTML）
│   └── preview.py            # 多主题预览生成器
├── styles/                   # 主题模板（HTML 文件）
│   ├── tech-dark-sidebar.html
│   ├── clean-minimal.html
│   └── notion.html
├── examples/demo.md          # 示例文档
└── assets/screenshots/       # 固定预览图
```

### 4.2 主题模板机制

每个主题都是一个标准 HTML 模板文件，内部使用以下占位符：

| 占位符 | 说明 |
|--------|------|
| `{{TITLE}}` | 文档标题（自动从首个 H1 提取） |
| `{{SUBTITLE}}` | 副标题（H1 后的引用或斜体段） |
| `{{TOC}}` | 侧栏目录 HTML（带编号、层级 class） |
| `{{TOC_BLOCK}}` | 内嵌目录卡片 HTML |
| `{{CONTENT}}` | 主体 HTML |

扩展新主题只需在 `styles/` 目录添加一个符合规范的 HTML 文件，并在 `STYLE_PRIORITY` 中注册。

### 4.3 Token 优化设计（重点）

这是本项目与一般"让 AI 直接生成 HTML"方案的本质区别：

**0 Token 的部分（纯脚本执行）**：

- Markdown 解析（使用 python-markdown 库）
- 标题提取与中文 slug 生成
- 代码高亮（Pygments）
- 模板占位符替换
- 最终 HTML 生成

**消耗 Token 的部分（AI 协调层）**：

- 识别用户触发词
- 调用 Shell 工具运行脚本
- 输出交互文本

对比表格：

| 方案 | 单次转换 Token 消耗 |
|------|--------------------|
| 让 AI 直接生成带样式的 HTML | 15,000 - 30,000 |
| md-couture（快速模式） | ~500 |
| md-couture（真实预览模式） | ~5,000 - 10,000 |

### 4.4 双模式预览设计

为了平衡"直观预览"和"Token 成本"，md-couture 采用双模式预览机制：

**快速模式（默认）**：

AI 仅返回仓库内 3 张固定样例截图的路径，不调用 Read 工具将图像载入对话。用户通过 cmd+click 打开本地图片查看。此模式下单次预览成本控制在 500 token 以内。

**真实模式（按需触发）**：

用户显式说"用我的文档预览"或"看看真实渲染效果"时，才调用 headless Chrome 渲染用户实际文档并截图。此模式 Token 消耗约 5-10K。

这种设计让用户在"是否想看真实效果"上**知情地付费**，比一刀切烧 token 的方案优雅得多。

### 4.5 缓存管理

所有中间产物（per-doc 截图、临时 demo HTML）都存储在 skill 自身的 `.cache/` 目录下，基于 `sha1(md绝对路径)[:10]` 命名子目录，保证：

- 同一文件多次运行覆盖同一缓存（不会膨胀）
- 不同文件互不干扰
- 每次运行自动清理 7 天以上未访问的子目录
- 用户工作区永远保持干净

## 五、Cursor Skill 开发心得

开发这个小工具的过程中，我对 Cursor Agent Skill 的能力边界有了更深的理解，在此分享三点心得：

### 5.1 Skill 的本质：自然语言触发的确定性执行

Agent Skill 的核心价值，**不是让 AI 创造性地解决问题**，而是让 AI 在识别到特定语义时，**触发预定义的确定性脚本**。所以 SKILL.md 中的 `description` 字段非常关键，它决定了 AI 判断"该不该用这个 skill"的准确性。

### 5.2 能用脚本就别让模型生成

每次调用 LLM 都是：
- 消耗 token
- 结果不完全一致
- 响应时间 >= 数秒

而脚本一次写好后：
- 0 token
- 输出 100% 一致
- 毫秒级响应

md-couture 的核心转换逻辑完全由 Python 脚本承担，AI 只负责触发识别和参数编排，这是我推荐的 skill 设计范式。

### 5.3 触发词要贴近真实用户表达

很多人写 SKILL.md 时喜欢用英文专业术语（"convert markdown to html"），但真实用户的表达其实是："转 html"、"美化这个"、"给我搞好看点"、"导出成网页"。

SKILL.md 的 `description` 字段一定要列全常见口语化说法，这样 AI 才能在各种表达下都稳定识别。

## 六、开源仓库

**GitHub 地址**：https://github.com/ronindong/md-couture

**License**：MIT（自由使用、修改、商用）

### 欢迎贡献

我特别希望社区能贡献更多主题：

- 📰 学术论文风（类 LaTeX、支持公式渲染）
- 🎨 杂志风（多栏、彩色标题）
- 💻 终端复古风（绿色等宽字体、CRT 感）
- 🎮 游戏风（霓虹配色、赛博朋克）
- 🏢 企业风（正式、深蓝、图表友好）

提 Issue 或 PR 都非常欢迎。

### 仓库截图示意

如果本文对你有帮助，欢迎在 GitHub 点个 Star ⭐。

## 七、结语

md-couture 只是我基于 Cursor Skill 做的众多小工具之一，但它很好地展示了 Agentic Skill 的价值：**用自然语言触发脚本的确定性执行**。相比直接让 AI "现场编代码"，这种方式更省 token、更稳定、更可维护。

希望这个工具能对同样热爱写 Markdown 的你有所帮助。如果你也在用 Cursor，推荐把它加到常用 skill 里，日常写完文档一句话就能美化导出。

最后再贴一下仓库地址：**https://github.com/ronindong/md-couture**

---

> 原创不易，如果觉得有用请一键三连（点赞 + 收藏 + 关注），你的支持是我继续分享的动力。  
> 遇到问题欢迎在 GitHub Issue 提问，或者在评论区留言交流。

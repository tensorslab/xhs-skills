---
name: xhs-note-creator
description: 小红书文字笔记创作与发布技能。适用于以文字内容为主的笔记场景（干货分享、知识科普、清单排行、教程步骤、资源推荐等）。本技能负责：(1) 撰写小红书笔记文案（标题+正文+标签），(2) 通过本地渲染脚本生成排版精美的图片卡片（8种CSS主题+4种分页模式），(3) 一键发布到小红书平台。触发关键词："写笔记"、"发小红书"、"发布笔记"、"文字笔记"、"小红书文案"、"撰写笔记"、"排版卡片"。注意：当用户需要 AI 生成插画/卡通/手绘风格的原创配图内容（非文字排版）时，应使用 baoyu-xhs-images 技能而非本技能。
---

# 小红书笔记创作技能

根据用户提供的资料或需求，创作小红书笔记内容、生成精美图片卡片，并可选择发布到小红书。

> 详细参数文档见 `references/params.md`

---

## 工作流程

### 第一步：撰写小红书笔记内容

根据用户需求和资料，创作符合小红书风格的内容：

**标题**：不超过 18 字，吸引眼球，可用数字/疑问句/感叹号增强吸引力。

**正文**：段落清晰，点缀少量 Emoji（每段 1-2 个），短句短段，结尾附 5-10 个 SEO 标签。不要使用任何 Markdown 语法！！只用 emoji、换行和全角符号排版。

---

### 第二步：生成渲染用 Markdown 文档

**注意：此 Markdown 专为图片渲染设计，禁止直接使用上一步的笔记正文。**

文档结构：

```markdown
---
emoji: "🚀"
title: "封面大标题（≤15字）"
subtitle: "封面副标题（≤15字）"
---

# 标题

内容...

---

# 标题

内容...

```

上方示例生成：一张封面（emoji + title + subtitle）+ 两张正文卡片（各自的 `#` 标题作为卡片标题）。

分页策略选择：
- 内容需精确切分 → 用 `---` 手动分隔，配合 `-m separator`
- 内容长短不稳定 → 生成普通 Markdown，使用 `-m auto-split`

---

### 第三步：选择主题风格

渲染前，**必须**向用户展示所有可用主题并让用户选择。使用 AskUserQuestion 工具，将 9 种主题作为选项列出：

| 编号 | 主题值 | 名称 | 视觉特征 |
|---|---|---|---|
| 1 | `sketch` | 手绘素描 | 手绘线条风格，温暖自然 |
| 2 | `default` | 默认简约 | 浅灰渐变背景，干净利落 |
| 3 | `playful-geometric` | 活泼几何 | Memphis 设计风格，色彩丰富 |
| 4 | `neo-brutalism` | 新粗野主义 | 粗框线条、强对比色块 |
| 5 | `botanical` | 植物园自然 | 绿植元素，自然清新 |
| 6 | `professional` | 专业商务 | 商务蓝色调，简洁正式 |
| 7 | `retro` | 复古怀旧 | 暖色调复古感，年代氛围 |
| 8 | `terminal` | 终端命令行 | 深色背景，代码终端风格 |
| 9 | `pink-notebook` | 粉色笔记本 | 粉色格子纸、手绘贴纸、玫瑰棕文字 |

**展示方式**：使用 AskUserQuestion 工具，将 9 种主题作为选项列出，每个选项包含名称和简短描述，等待用户选择后再进入渲染步骤。

---

### 第四步：渲染图片卡片

根据用户在第三步选择的主题，执行渲染命令：

```bash
python scripts/render_xhs.py <markdown_file> -t <用户选择的主题> [options]
```

**默认分页**：`separator`（按 `---` 分隔）

常用示例：

```bash
# 使用用户选择的主题 + 手动分页
python scripts/render_xhs.py content.md -t sketch

# 自动分页（推荐内容长短不定时）
python scripts/render_xhs.py content.md -t playful-geometric -m auto-split
```

生成结果：`cover.png`（封面）+ `card_1.png`、`card_2.png`...（正文卡片）

**分页模式**（`-m`）：`separator`、`auto-split`、`dynamic`

> 完整参数说明见 `references/params.md`

---

### 第五步：发布小红书笔记（可选）

#### 5.1 Cookie 配置（首次发布前）

检查 `.env` 中是否已配置有效的 `XHS_COOKIE`。若未配置或已过期，引导用户登录获取：

**优先使用内置浏览器（yobrowser MCP 工具）**：

1. 打开小红书登录页：

```
yobrowser_load_url(url="https://www.xiaohongshu.com")
```

2. 提示用户在浏览器中完成登录操作，等待用户确认登录完成。

3. 登录完成后，通过 CDP 获取完整 Cookie（包含 httpOnly 的 `web_session`）：

```
yobrowser_cdp_send(method="Network.getAllCookies")
```

4. 将获取到的 Cookie 拼接为字符串（`key1=value1; key2=value2; ...`），保存到 `.env` 文件。

**yobrowser 不可用时**：直接运行发布脚本，脚本会自动启动 `quick_login.py` 获取 Cookie：

```bash
python scripts/publish_xhs.py --title "标题" --note note.md --images cover.png card_1.png
```

脚本检测到 Cookie 缺失或无效（缺少 `a1`/`web_session`）时，自动调用 `scripts/quick_login.py` 打开 Chromium 浏览器，用户登录后自动获取 Cookie 并保存到 `.env`，然后继续发布流程。

**也可独立运行 Cookie 获取脚本**（如 Cookie 过期需单独刷新）：

```bash
python scripts/quick_login.py
```

**关键点**：
- 必须使用 `Network.getAllCookies`（CDP）或 Playwright `context.cookies()`，不能用 `document.cookie`（无法获取 httpOnly 的 `web_session`）
- 有效 Cookie 必须包含 `a1` 和 `web_session` 两个关键字段
- `.env` 文件查找路径：当前工作目录 → skill 目录 → 项目根目录

#### 5.2 发布笔记

所有笔记一律以**仅自己可见**方式发布，用户在小红书中确认内容无误后再自行公开。

```bash
# 从方案文件读取描述 + 单独指定标题（推荐，与第一步的输出对接）
python scripts/publish_xhs.py --title "笔记标题" --note note.md --images cover.png card_1.png card_2.png

# 手动指定标题和描述
python scripts/publish_xhs.py --title "笔记标题" --desc "笔记描述" \
  --images cover.png card_1.png card_2.png
```

`--title` 为必填参数（不超过20字），超出将报错并拒绝发布。`--note` 文件内容作为描述正文，`--desc` 为手动指定描述。两者同时传入时以 `--note` 文件为准。

**禁止**将第二步生成的渲染用 Markdown 文件传给 `--note`。`--note` 必须指向第一步生成的纯文本笔记内容，因为渲染用 Markdown 包含 YAML 头部和 `---` 分隔符等排版语法，不适合作为笔记描述。

发布成功后会返回笔记 ID 和链接，用户可在小红书 App 或网页中预览确认。

---

## 技能资源

### 脚本
- `scripts/render_xhs.py` — 渲染脚本（主推，9 主题 + 4 分页模式）
- `scripts/render_xhs_v2.py` — 渲染脚本 V2（备用，7 种渐变色彩风格）
- `scripts/publish_xhs.py` — 发布脚本
- `scripts/quick_login.py` — Cookie 获取脚本（浏览器登录，自动保存到 `.env`）

### 模板与样式
- `assets/cover.html` — 封面 HTML 模板
- `assets/card.html` — 正文卡片 HTML 模板
- `assets/styles.css` — 公共容器样式
- `assets/themes/` — 各主题 CSS 文件

### 参考文档
- `references/params.md` — 完整参数参考（主题/模式/发布参数）

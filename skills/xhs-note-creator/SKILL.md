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

**标题**：不超过 20 字，吸引眼球，可用数字/疑问句/感叹号增强吸引力。

**正文**：段落清晰，点缀少量 Emoji（每段 1-2 个），短句短段，结尾附 5-10 个 SEO 标签。

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

# 正文内容...

---

# 第二张卡片内容...（使用 --- 手动分隔时）
```

分页策略选择：
- 内容需精确切分 → 用 `---` 手动分隔，配合 `-m separator`
- 内容长短不稳定 → 生成普通 Markdown，使用 `-m auto-split`

---

### 第三步：渲染图片卡片

```bash
python scripts/render_xhs.py <markdown_file> [options]
```

**默认主题**：`sketch`（手绘素描风格）  
**默认分页**：`separator`（按 `---` 分隔）

常用示例：

```bash
# 默认（sketch 主题 + 手动分页）
python scripts/render_xhs.py content.md

# 自动分页（推荐内容长短不定时）
python scripts/render_xhs.py content.md -m auto-split

# 切换主题
python scripts/render_xhs.py content.md -t playful-geometric -m auto-split

# 固定尺寸自动缩放
python scripts/render_xhs.py content.md -m auto-fit
```

生成结果：`cover.png`（封面）+ `card_1.png`、`card_2.png`...（正文卡片）

**可用主题**（`-t`）：`sketch`、`default`、`playful-geometric`、`neo-brutalism`、`botanical`、`professional`、`retro`、`terminal`

**分页模式**（`-m`）：`separator`、`auto-fit`、`auto-split`、`dynamic`

> 完整参数说明见 `references/params.md`

---

### 第四步：发布小红书笔记（可选）

#### 4.1 Cookie 配置（首次发布前）

检查 `.env` 中是否已配置有效的 `XHS_COOKIE`。若未配置或已过期，通过内置浏览器引导用户登录获取：

1. 使用内置浏览器打开小红书登录页：

```
yobrowser_load_url(url="https://www.xiaohongshu.com")
```

2. 提示用户在浏览器中完成登录操作，等待用户确认登录完成。

3. 登录完成后，通过 CDP 获取完整 Cookie（包含 httpOnly 的 `web_session`）：

```
yobrowser_cdp_send(method="Network.getAllCookies")
```

4. 将获取到的 Cookie 拼接为字符串（`key1=value1; key2=value2; ...`），保存到 `.env` 文件：

```
XHS_COOKIE=abRequestId=...; web_session=...; a1=...; webId=...; ...
```

**关键点**：
- 必须使用 `Network.getAllCookies`（CDP），不能用 `document.cookie`（无法获取 httpOnly 的 `web_session`）
- 有效 Cookie 必须包含 `a1` 和 `web_session` 两个关键字段
- `.env` 文件查找路径：当前工作目录 → skill 目录 → 项目根目录

#### 4.2 发布笔记

所有笔记一律以**仅自己可见**方式发布，用户在小红书中确认内容无误后再自行公开。

```bash
# 从方案文件读取文案（推荐，与第一步的输出对接）
python scripts/publish_xhs.py --note note.md --images cover.png card_1.png card_2.png

# 手动指定标题和描述
python scripts/publish_xhs.py --title "笔记标题" --desc "笔记描述" \
  --images cover.png card_1.png card_2.png
```

`--note` 和 `--title`/`--desc` 同时传入时，以 `--note` 文件内容为准。方案文件支持含 YAML frontmatter 的 Markdown（提取 `title` 字段 + 正文）或纯文本（第一行为标题，其余为描述）。

发布成功后会返回笔记 ID 和链接，用户可在小红书 App 或网页中预览确认。

---

## 技能资源

### 脚本
- `scripts/render_xhs.py` — 渲染脚本（主推，8 主题 + 4 分页模式）
- `scripts/render_xhs_v2.py` — 渲染脚本 V2（备用，7 种渐变色彩风格）
- `scripts/publish_xhs.py` — 发布脚本

### 模板与样式
- `assets/cover.html` — 封面 HTML 模板
- `assets/card.html` — 正文卡片 HTML 模板
- `assets/styles.css` — 公共容器样式
- `assets/themes/` — 各主题 CSS 文件

### 参考文档
- `references/params.md` — 完整参数参考（主题/模式/发布参数）

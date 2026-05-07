# 参数参考文档

## 渲染脚本（render_xhs.py）

```bash
python scripts/render_xhs.py <markdown_file> [options]
```

### 参数列表

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--output-dir` | `-o` | 输出目录 | 当前工作目录 |
| `--theme` | `-t` | 排版主题 | `sketch` |
| `--mode` | `-m` | 分页模式 | `separator` |
| `--width` | `-w` | 图片宽度（px） | `1080` |
| `--height` | | 图片高度（`dynamic` 下为最小高度） | `1440` |
| `--max-height` | | `dynamic` 模式下的最大高度 | `4320` |
| `--dpr` | | 设备像素比（清晰度） | `2` |

### 排版主题（`--theme`）

| 值 | 名称 | 说明 |
|---|---|---|
| `sketch` | 手绘素描 | 手绘风格，默认 |
| `default` | 默认简约 | 浅灰渐变背景（`#f3f3f3 → #f9f9f9`） |
| `playful-geometric` | 活泼几何 | Memphis 设计风格 |
| `neo-brutalism` | 新粗野主义 | 粗框线条、强对比 |
| `botanical` | 植物园自然 | 自然绿植风格 |
| `professional` | 专业商务 | 简洁商务蓝 |
| `retro` | 复古怀旧 | 暖色复古感 |
| `terminal` | 终端命令行 | 深色代码终端风格 |

### 分页模式（`--mode`）

| 值 | 说明 | 适用场景 |
|---|---|---|
| `separator` | 按 `---` 分隔符分页 | 内容已手动控量，需要精确分页 |
| `auto-fit` | 固定尺寸，自动整体缩放内容 | 封面 + 单张图，尺寸固定不溢出 |
| `auto-split` | 根据渲染后高度自动切分 | 内容长短不稳定，推荐通用选择 |
| `dynamic` | 根据内容动态调整图片高度 | 允许不同高度卡片，字数 ≤550 |

### 常用命令示例

```bash
# 默认：sketch 主题 + 手动分隔分页
python scripts/render_xhs.py content.md

# 自动分页（推荐内容不稳定时使用）
python scripts/render_xhs.py content.md -m auto-split

# 固定尺寸自动缩放
python scripts/render_xhs.py content.md -m auto-fit

# 切换主题
python scripts/render_xhs.py content.md -t playful-geometric -m auto-split

# 自定义尺寸
python scripts/render_xhs.py content.md -t retro -m dynamic --width 1080 --height 1440 --dpr 2
```

---

## 发布脚本（publish_xhs.py）

```bash
python scripts/publish_xhs.py --title "标题" --desc "描述" --images img1.png img2.png
```

### 参数列表

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--note` | `-n` | 方案文件路径（Markdown/纯文本，从中读取 title 和 desc） | 可选 |
| `--title` | `-t` | 笔记标题（不超过 20 字，`--note` 优先） | 可选* |
| `--desc` | `-d` | 笔记描述/正文内容（`--note` 优先） | `""` |
| `--images` | `-i` | 图片文件路径（可多个） | 必填 |
| `--post-time` | | 定时发布（格式：`2024-01-01 12:00:00`） | 立即发布 |
| `--api-mode` | | 通过 xhs-api 服务发布 | 本地模式 |
| `--api-url` | | API 服务地址 | `http://localhost:5005` |
| `--dry-run` | | 仅验证，不实际发布 | `False` |

> *`--note` 和 `--title` 至少提供一个。两者同时传入时以 `--note` 文件内容为准。
> 所有笔记一律以「仅自己可见」发布，用户在小红书中确认后再自行公开。

### 方案文件格式

支持两种格式：

**1. 含 YAML frontmatter 的 Markdown（推荐）：**

```markdown
---
title: "5个效率神器"
---

正文内容...
```

提取 `title` 字段作为标题，frontmatter 之后的正文作为描述。

**2. 纯文本：**

```
5个效率神器
正文内容...
```

第一行作为标题（不超过 20 字），其余行作为描述。

### 常用命令示例

```bash
# 从方案文件读取文案（推荐）
python scripts/publish_xhs.py --note note.md --images cover.png card_1.png card_2.png

# 手动指定标题和描述
python scripts/publish_xhs.py --title "标题" --desc "描述" --images cover.png card_1.png

# 定时发布
python scripts/publish_xhs.py --note note.md --images *.png --post-time "2024-12-01 10:00:00"

# API 模式
python scripts/publish_xhs.py --note note.md --images *.png --api-mode

# 仅验证不发布
python scripts/publish_xhs.py --note note.md --images *.png --dry-run
```

### 环境变量配置（.env）

```bash
cp env.example.txt .env
```

编辑 `.env`：

```env
# 必需：小红书 Cookie（需包含 a1 和 web_session）
XHS_COOKIE=abRequestId=...; web_session=...; a1=...; webId=...; ...

# 可选：API 模式服务地址
XHS_API_URL=http://localhost:5005
```

**Cookie 获取方式**：优先通过内置浏览器 yobrowser（MCP 工具）获取，不可用时脚本自动回退到 Playwright。

- **yobrowser 方式**（由 Agent 执行）：`yobrowser_load_url` → 用户登录 → `yobrowser_cdp_send(method="Network.getAllCookies")` → 保存到 `.env`
- **Playwright fallback**（脚本自动触发）：启动 Chromium → 用户登录 → `context.cookies()` → 保存到 `.env`

> `.env` 文件查找路径：当前工作目录 → skill 目录 → 项目根目录

---

## Markdown 文档格式

### YAML 头部元数据

```yaml
---
emoji: "🚀"           # 封面装饰 Emoji
title: "大标题"        # 封面大标题（不超过 15 字）
subtitle: "副标题文案"  # 封面副标题（不超过 15 字）
---
```

### 分页分隔符

使用 `---` 手动分割卡片（配合 `-m separator` 使用）：

```markdown
---
emoji: "💡"
title: "工具推荐"
subtitle: "提升效率的 5 个神器"
---

# 神器一：Notion

> 全能笔记工具...

---

# 神器二：Raycast

快捷启动工具...
```

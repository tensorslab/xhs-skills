## xhs-skills

### ⚠️ 使用此工具前请确保已悉知官方 3 月 10 日发布的公告

公告地址：[关于打击AI托管运营账号的治理公告](http://xhslink.com/o/7WxTddvbmTu)

---

仓库地址：[https://github.com/tensorslab/xhs-skills.git](https://github.com/tensorslab/xhs-skills.git)

本项目基于 Skills 工作流重新组织了小红书内容创作、图片生成与发布能力。当前仓库相对于原上游仓库在目录结构、技能拆分、提示词协作方式、发布流程和方案展示细节上都已发生较大变化；原上游仓库已移入[致谢](#致谢)列表。

项目包含两个小红书创作技能，各司其职，并共享同一套发布能力：

| 技能                  | 定位                           | 适用场景                                             |
| --------------------- | ------------------------------ | ---------------------------------------------------- |
| **xhs-note-creator**  | 文字类小红书创作与发布         | 撰写文案 → 专业化排版渲染卡片 → 私密推送到小红书     |
| **xhs-images-design** | 图片类小红书图文卡片生成与发布 | AI 生成插画/卡通/手绘风格原创配图 → 私密推送到小红书 |

核心能力：

- 扫码登录小红书后，可将生成内容自动推送到小红书。
- 发布默认采用「仅自己可见」，不会直接公开；用户可在小红书中确认后再自行公开。
- 文字类与图片类内容分别由两个 skill 处理，提示词已调整为更协调的协作关系。
- 方案展示细节经过专业化改造，更适合内容确认、风格选择和后续复用。

---

## 安装

### 方式一：Claude Code Plugin 安装（推荐）

```bash
# 添加本仓库为 marketplace
/plugin marketplace add tensorslab/xhs-skills

# 安装插件
/plugin install xhs-skills@tensorslab-xhs-skills
```

安装后运行 `/reload-plugins` 即可使用。

### 方式二：一句话安装

跟你的 Agent 说：

> 拉取下面的项目，安装其中的技能：https://github.com/tensorslab/xhs-skills.git

### 方式三：手动安装

```bash
git clone https://github.com/tensorslab/xhs-skills.git
cd xhs-skills
```

可以将本项目放到支持 Skills 的客户端目录，例如：

- Claude：`~/.claude/skills/`
- Alma：`~/.config/Alma/skills/`
- TRAE：`/your-path/.trae/skills/`

### 安装依赖

**Python：**

```bash
pip install -r requirements.txt
playwright install chromium
```

**Node.js：**

```bash
npm install
npx playwright install chromium
```

---

## 技能一：xhs-note-creator（文字类小红书创作与发布）

以文字内容为主的笔记场景：干货分享、知识科普、清单排行、教程步骤等。

### 工作流程

1. 撰写小红书笔记文案（标题 + 正文 + 标签）
2. 生成渲染用 Markdown 文档
3. 通过本地脚本渲染专业化图片卡片（9 种主题 + 多种分页模式）
4. 扫码登录后，可自动推送到小红书（默认仅自己可见）

### 渲染图片（Python）

核心脚本：`skills/xhs-note-creator/scripts/render_xhs.py`

```bash
# 最简单用法（默认主题 + 手动分页）
python skills/xhs-note-creator/scripts/render_xhs.py demos/content.md

# 使用自动分页（推荐：内容长短难控）
python skills/xhs-note-creator/scripts/render_xhs.py demos/content.md -m auto-split

# 使用固定尺寸自动缩放（auto-fit）
python skills/xhs-note-creator/scripts/render_xhs.py demos/content_auto_fit.md -m auto-fit

# 切换主题（例如 Playful Geometric）
python skills/xhs-note-creator/scripts/render_xhs.py demos/content.md -t playful-geometric -m auto-split

# 自定义尺寸和像素比
python skills/xhs-note-creator/scripts/render_xhs.py demos/content.md -t retro -m dynamic --width 1080 --height 1440 --max-height 2160 --dpr 2
```

**主要参数：**

| 参数           | 简写 | 说明                                                                                                                                   |
| -------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `--theme`      | `-t` | 可用主题：`default`、`playful-geometric`、`neo-brutalism`、`botanical`、`professional`、`retro`、`terminal`、`sketch`、`glassmorphism` |
| `--mode`       | `-m` | 分页模式：`separator` / `auto-fit` / `auto-split` / `dynamic`                                                                          |
| `--width`      | `-w` | 图片宽度（默认 1080）                                                                                                                  |
| `--height`     |      | 图片高度（默认 1440，`dynamic` 为最小高度）                                                                                            |
| `--max-height` |      | `dynamic` 模式最大高度（默认 2160）                                                                                                    |
| `--dpr`        |      | 设备像素比，控制清晰度（默认 2）                                                                                                       |

> 生成结果：封面 `cover.png` + 正文卡片 `card_1.png`、`card_2.png`...

### 渲染图片（Node.js）

脚本：`skills/xhs-note-creator/scripts/render_xhs.js`，参数与 Python 基本一致：

```bash
# 默认主题 + 手动分页
node skills/xhs-note-creator/scripts/render_xhs.js demos/content.md

# 指定主题 + 自动分页
node skills/xhs-note-creator/scripts/render_xhs.js demos/content.md -t terminal -m auto-split
```

### 发布到小红书

发布脚本会始终以「仅自己可见」方式发布，内容不会直接公开。用户可在小红书 App 或网页中确认效果后，再手动调整为公开。

**1. 扫码登录 / 配置 Cookie**

```bash
cp env.example.txt .env
```

编辑 `.env`：

```env
XHS_COOKIE=your_cookie_string_here
```

> 获取方式：运行 `python skills/xhs-note-creator/scripts/quick_login.py`，扫码登录后自动获取。

**2. 发布**

```bash
# 从方案文件读取文案（推荐）
python skills/xhs-note-creator/scripts/publish_xhs.py \
  --title "笔记标题" --note note.md --images cover.png card_1.png card_2.png

# 手动指定标题和描述
python skills/xhs-note-creator/scripts/publish_xhs.py \
  --title "笔记标题" --desc "笔记描述" --images cover.png card_1.png
```

**可选参数：**

| 参数                                | 说明                                           |
| ----------------------------------- | ---------------------------------------------- |
| `--note`                            | 方案文件路径（Markdown/纯文本，从中读取 desc） |
| `--post-time "2024-01-01 12:00:00"` | 定时发布                                       |
| `--api-mode`                        | 通过 xhs-api 服务发布                          |
| `--dry-run`                         | 仅验证，不实际发布                             |

### 主题效果示例

> 所有示例均为 1080x1440px，小红书推荐 3:4 比例
> 更多示例去 [demo](/demos) 中查看

|                                                          |                                        |
| -------------------------------------------------------- | -------------------------------------- |
| ![Playful Geometric](demos/playful-geometric/card_1.png) | ![Retro](demos/retro/card_1.png)       |
| ![Sketch](demos/Sketch/card_1.png)                       | ![Terminal](demos/terminal/card_1.png) |

### Auto-fit 模式示例（自动缩放）

![Auto Fit](demos/auto-fit/card_1.png)

---

## 技能二：xhs-images-design（图片类小红书图文卡片生成与发布）

AI 生成插画/卡通/手绘配图的图文并茂内容：种草分享、手绘笔记、知识图解、视觉冲击封面等。

支持 12 种视觉风格、8 种信息布局和 3 种配色方案，通过 AI 图像生成工具创建 1-10 张风格化图片卡片。该 skill 已加入本项目的整体小红书工作流，并与 `xhs-note-creator` 的提示词边界保持协调：文字类内容优先走 `xhs-note-creator`，需要 AI 原创配图、图解或视觉化表达时走 `xhs-images-design`。

生成图片后，可复用 `xhs-note-creator` 的发布脚本进行小红书私密推送：

```bash
python skills/xhs-note-creator/scripts/publish_xhs.py \
  --title "笔记标题" --desc "笔记描述" --images image-cards/topic/01-cover.png image-cards/topic/02-content.png
```

详见 `skills/xhs-images-design/SKILL.md`。

---

## 项目结构

```
xhs-skills/
├── README.md                         # 项目文档
├── requirements.txt                  # Python 依赖
├── package.json                      # Node.js 依赖
├── env.example.txt                   # Cookie 配置示例
├── demos/                            # 各主题示例渲染结果
│   ├── content.md
│   ├── content_auto_fit.md
│   ├── auto-fit/
│   ├── playful-geometric/
│   ├── retro/
│   ├── Sketch/
│   └── terminal/
├── skills/
│   ├── xhs-note-creator/             # 文字类小红书技能
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── render_xhs.py         # Python 渲染（9 主题 + 多种分页）
│   │   │   ├── render_xhs_v2.py      # Python 渲染 V2（渐变色彩风格）
│   │   │   ├── render_xhs.js         # Node.js 渲染
│   │   │   ├── render_xhs_v2.js      # Node.js 渲染 V2
│   │   │   ├── quick_login.py        # 扫码登录并获取 Cookie
│   │   │   └── publish_xhs.py        # 小红书私密发布脚本
│   │   ├── assets/
│   │   │   ├── cover.html            # 封面 HTML 模板
│   │   │   ├── card.html             # 正文卡片 HTML 模板
│   │   │   ├── styles.css            # 公共容器样式
│   │   │   ├── example.md            # 示例 Markdown
│   │   │   └── themes/               # 主题样式
│   │   └── references/
│   │       └── params.md             # 完整参数参考
│   └── xhs-images-design/            # 图片类小红书图文卡片技能
│       ├── SKILL.md
│       └── references/               # 风格/布局/配色参考文档
```

---

## 注意事项

1. **Cookie 安全**：不要把 `.env` 提交到 Git 或共享出去。
2. **Cookie 有效期**：过期后发布失败是正常现象，重新抓一次 Cookie 即可。
3. **默认私密发布**：自动推送到小红书后默认仅自己可见，不会直接公开。
4. **发布频率**：避免短时间内高频发布，以免触发平台风控。
5. **图片尺寸**：默认 1080x1440px，符合小红书推荐比例。

---

## 致谢

- [comeonzhj/Auto-Redbook-Skills](https://github.com/comeonzhj/Auto-Redbook-Skills) - 原上游仓库，为本项目早期形态提供了重要基础
- [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) - `xhs-images-design` 原始技能来源，感谢 JimLiu 的出色工作
- [Playwright](https://playwright.dev/) - 浏览器自动化渲染
- [Marked](https://marked.js.org/) - Markdown 解析
- [xhs](https://github.com/ReaJason/xhs) - 小红书 API 客户端

---

## License

MIT License

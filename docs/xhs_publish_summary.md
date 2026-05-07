# 小红书笔记发布 - 问题总结与解决方案

## 一、获取 Cookie 的完整流程

### 1.1 初始尝试：通过 JavaScript 获取

**方法：** 使用 CDP 命令 `Runtime.evaluate` 执行 `document.cookie`

**问题：**
- 只能获取到基础 cookies（abRequestId、ets、a1、webId、gid等）
- 缺少关键的 `web_session` 字段
- 小红书发布笔记需要 `web_session` 进行身份验证

### 1.2 尝试方案：从 Chrome 数据库读取

**方法：**
```bash
# 尝试复制 Chrome cookies 数据库文件
Copy-Item "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Network\Cookies" "chrome_cookies.db"
```

**问题：**
- 文件被 Chrome 进程占用，无法直接复制
- 报错：`The process cannot access the file...because it is being used by another process`

### 1.3 最终解决方案：使用 CDP Network API

**方法：** 使用 CDP 命令 `Network.getAllCookies`

**命令：**
```python
yobrowser_cdp_send(method="Network.getAllCookies")
```

**结果：** ✅ 成功获取完整的 cookies，包含 `web_session` 字段

**获取到的关键 cookies：**
```
web_session=040069b4589e38fe6894a44cc93b4b77668d89
a1=19df1ec1b0c34fi8lboyls5avt8mpf2p02ox3cfap50000105868
webId=940c177a8701f34315c5398a6376f256
...
```

### 1.4 Cookie 配置

将完整 cookies 保存到 `.env` 文件：
```env
XHS_COOKIE=abRequestId=...; web_session=...; a1=...; webId=...
```

## 二、函数签名问题与修复

### 2.1 问题描述

**错误信息：**
```
❌ 发布失败: LocalPublisher.init_client.<locals>.sign_func() got an unexpected keyword argument 'a1'
```

### 2.2 问题根源

**原代码（publish_xhs.py:141-143）：**
```python
def sign_func(uri, data=None, a1_param="", web_session=""):
    # 使用 cookie 中的 a1 值
    return local_sign(uri, data, a1=a1 or a1_param)
```

**问题分析：**
1. 签名函数参数名为 `a1_param`
2. 但调用 `local_sign` 时使用的是 `a1` 参数
3. 这导致 xhs 库在调用 sign_func 时传递的参数名不匹配

### 2.3 解决方案

**修改后的代码：**
```python
def sign_func(uri, data=None, a1="", web_session=""):
    # 使用 cookie 中的 a1 值
    return local_sign(uri, data, a1=a1 or a1)
```

**修改要点：**
- 将参数名从 `a1_param` 改为 `a1`
- 保持与 `local_sign` 函数调用的参数名一致

## 三、完整发布流程

### 3.1 准备阶段

1. **打开内置浏览器并访问小红书**
   ```python
   yobrowser_load_url(url="https://www.xiaohongshu.com")
   ```

2. **用户完成登录**

3. **获取完整 Cookies**
   ```python
   yobrowser_cdp_send(method="Network.getAllCookies")
   ```

4. **配置环境变量**
   ```env
   XHS_COOKIE=完整cookie字符串
   ```

### 3.2 发布阶段

1. **生成图片卡片**
   ```bash
   python scripts/render_xhs.py content.md -t sketch -m separator
   ```

2. **发布到小红书**
   ```bash
   python scripts/publish_xhs.py --title "标题" --desc "描述" --images cover.png card_1.png ...
   ```

### 3.3 发布结果

```
✨ 笔记发布成功！
  📎 笔记ID: 69fc078c0000000035023a4f
  🔗 链接: https://www.xiaohongshu.com/explore/69fc078c0000000035023a4f
```

## 四、技术要点总结

### 4.1 Cookie 获取

| 方法 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| `document.cookie` | 简单直接 | 无法获取 httpOnly cookies | ⭐⭐ |
| Chrome 数据库读取 | 可获取所有 cookies | 文件被占用，需关闭浏览器 | ⭐⭐⭐ |
| `Network.getAllCookies` | 获取完整 cookies，不关闭浏览器 | 需要使用 CDP | ⭐⭐⭐⭐⭐ |

### 4.2 函数签名规范

**关键原则：**
1. 签名函数的参数名必须与底层库调用的参数名一致
2. 参数命名要遵循清晰、一致的原则
3. 避免使用 `_param` 等后缀造成混淆

### 4.3 小红书 Cookie 验证

**必需字段：**
- `a1` - 用户标识
- `web_session` - 会话令牌（httpOnly，关键）

**可选字段：**
- `webId` - Web 设备 ID
- `gid` - 全球标识符
- `xsecappid` - 应用标识

## 五、经验教训

1. **httpOnly Cookies 无法通过 JavaScript 获取**
   - `web_session` 是 httpOnly cookie
   - 必须使用浏览器 DevTools Protocol 或直接读取数据库

2. **Chrome 数据库文件被占用**
   - 运行中的 Chrome 进程会锁定 cookies 文件
   - 使用 CDP API 可以绕过这个问题

3. **函数参数名一致性**
   - 桥接函数的参数名必须与目标函数匹配
   - 参数命名要清晰明确，避免歧义

4. **调试技巧**
   - 从错误信息中快速定位参数不匹配问题
   - 修改后立即测试验证

## 六、参考资料

- 小红书 API 文档
- Chrome DevTools Protocol 文档
- Python xhs 库使用说明
#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("缺少依赖，请运行: pip install playwright python-dotenv && playwright install chromium")
    sys.exit(1)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.xiaohongshu.com")
        print("\n🌐 请在浏览器中完成小红书登录...")
        print("💡 登录成功后，脚本将自动获取 Cookie 并保存到 .env 文件\n")

        # 记录页面加载后的初始 web_session 值
        initial_cookies = await context.cookies()
        initial_ws = {c["name"]: c["value"] for c in initial_cookies}.get("web_session", "")

        # 阶段1：等待 web_session 变化（登录完成）
        cookie_string = ""
        while True:
            if not browser.is_connected():
                break

            cookies = await context.cookies()
            cookies_dict = {c["name"]: c["value"] for c in cookies}
            current_ws = cookies_dict.get("web_session", "")

            # web_session 出现新值（从未登录到登录，或值发生变化）
            if current_ws and current_ws != initial_ws:
                print("✅ 检测到登录成功，等待 Cookie 稳定...")
                # 阶段2：等 JS 生成完整 cookie（gid 等）
                await asyncio.sleep(5)

                cookies = await context.cookies()
                cookies_dict = {c["name"]: c["value"] for c in cookies}

                if "web_session" not in cookies_dict or "a1" not in cookies_dict:
                    print("⚠️ Cookie 异常，缺少 web_session 或 a1")
                    break

                if "gid" not in cookies_dict:
                    print("⚠️ Cookie 中缺少 gid，部分接口可能无法调用")

                cookie_string = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
                break

            await asyncio.sleep(2)

        if cookie_string:
            env_path = Path(".env")
            if env_path.exists():
                lines = env_path.read_text(encoding="utf-8").splitlines()
                lines = [l for l in lines if not l.startswith("XHS_COOKIE=")]
                lines.append(f"XHS_COOKIE={cookie_string}")
                content = "\n".join(lines) + "\n"
            else:
                content = f"XHS_COOKIE={cookie_string}\n"

            env_path.write_text(content, encoding="utf-8")
            print(f"\n✅ 成功获取 Cookie 并保存至 {env_path.absolute()}")
        else:
            print("\n❌ 未能获取有效 Cookie")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

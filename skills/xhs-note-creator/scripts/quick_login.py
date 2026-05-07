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
        print("💡 登录成功后，脚本将自动获取 Cookie 并保存到 .env 文件")

        # 持续检查是否包含关键 cookie
        cookie_string = ""
        while True:
            cookies = await context.cookies()
            cookies_dict = {c["name"]: c["value"] for c in cookies}

            if "web_session" in cookies_dict and "a1" in cookies_dict:
                cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                break

            await asyncio.sleep(2)
            # 如果浏览器关闭了则退出
            if browser.is_connected() is False:
                break

        if cookie_string:
            env_path = Path(".env")
            content = f"XHS_COOKIE={cookie_string}\n"

            if env_path.exists():
                lines = env_path.read_text(encoding="utf-8").splitlines()
                new_lines = [line for line in lines if not line.startswith("XHS_COOKIE=")]
                new_lines.append(f"XHS_COOKIE={cookie_string}")
                content = "\n".join(new_lines) + "\n"

            env_path.write_text(content, encoding="utf-8")
            print(f"\n✅ 成功获取 Cookie 并保存至 {env_path.absolute()}")
        else:
            print("\n❌ 未能获取有效 Cookie")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

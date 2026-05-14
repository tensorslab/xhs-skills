#!/usr/bin/env python3
import argparse
import asyncio
import os
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("缺少依赖，请运行: pip install playwright python-dotenv && playwright install chromium")
    sys.exit(1)


def _default_env_path() -> Path:
    """默认保存到当前项目；若运行在 skill 内，则保存到 skill 同级父目录。"""
    skill_dir = Path(__file__).parent.parent.resolve()
    cwd = Path.cwd().resolve()
    if cwd == skill_dir or skill_dir in cwd.parents:
        return skill_dir.parent / ".env"
    return cwd / ".env"


def parse_args():
    parser = argparse.ArgumentParser(description="登录小红书并保存 Cookie 到 .env")
    parser.add_argument(
        "--env-path",
        default=os.getenv("XHS_ENV_PATH") or str(_default_env_path()),
        help="Cookie 保存路径（默认: 当前项目 .env；若运行在 skill 内，则保存到 skill 同级父目录）",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    env_path = Path(args.env_path).expanduser().resolve()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.xiaohongshu.com")
        print("\n🌐 请在浏览器中完成小红书登录...")
        print(f"💡 登录成功后，脚本将自动获取 Cookie 并保存到 {env_path}\n")

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
            env_path.parent.mkdir(parents=True, exist_ok=True)
            if env_path.exists():
                lines = env_path.read_text(encoding="utf-8").splitlines()
                lines = [line for line in lines if not line.startswith("XHS_COOKIE=")]
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

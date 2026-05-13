"""XHS Cookie 过期检测与清理工具"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional


def parse_cookie(cookie_string: str) -> Dict[str, str]:
    """解析 Cookie 字符串为字典"""
    cookies = {}
    for item in cookie_string.split(";"):
        item = item.strip()
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def is_cookie_expired(env_path: Optional[Path], max_age_hours: float = 24) -> bool:
    """基于 .env 文件最后修改时间判断 Cookie 是否过期。

    XHS 的 web_session 通常 24 小时过期，a1 约 30 天。
    Cookie 内的 ets/loadts 可能早于本次保存时间，因此以 .env mtime 为准。
    """
    if env_path is None or not env_path.exists():
        return False

    timestamp = env_path.stat().st_mtime
    age_hours = (time.time() - timestamp) / 3600
    if age_hours > max_age_hours:
        from datetime import datetime

        modified = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
        print(f"⚠️ Cookie 已过期（.env 修改于 {modified}，已 {age_hours:.1f} 小时，阈值 {max_age_hours}h）")
        return True
    return False


def remove_cookie_from_all_envs(env_paths: List[Path]) -> List[str]:
    """从所有候选 .env 文件中移除 XHS_COOKIE 行，同时清除 os.environ。"""
    removed_from = []
    for env_path in env_paths:
        if not env_path.exists():
            continue
        lines = env_path.read_text(encoding="utf-8").splitlines()
        new_lines = [line for line in lines if not line.startswith("XHS_COOKIE=")]
        if len(new_lines) < len(lines):
            content = "\n".join(new_lines)
            if content and not content.endswith("\n"):
                content += "\n"
            elif not content:
                content = ""
            env_path.write_text(content, encoding="utf-8")
            removed_from.append(str(env_path))

    if "XHS_COOKIE" in os.environ:
        del os.environ["XHS_COOKIE"]

    if removed_from:
        print("🗑️ 已从以下位置删除过期 Cookie:")
        for p in removed_from:
            print(f"   - {p}")

    return removed_from

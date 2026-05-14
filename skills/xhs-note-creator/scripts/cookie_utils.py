"""XHS Cookie 工具：路径解析、过期检测、清理。"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional

# 本文件位于 .../skills/xhs-note-creator/scripts/cookie_utils.py
# parents[2] = skills/（所有 skill 的同级父目录，.env 保存在此）
_SKILL_PARENT_DIR = Path(__file__).resolve().parents[2]


def get_default_env_path() -> Path:
    """默认 .env 路径：skill 同级父目录下的 .env（不依赖 CWD）。"""
    return _SKILL_PARENT_DIR / ".env"


def get_env_paths() -> List[Path]:
    """返回 .env 候选路径列表（按优先级）。"""
    paths: List[Path] = []
    configured = os.getenv("XHS_ENV_PATH")
    if configured:
        paths.append(Path(configured).expanduser().resolve())
    paths.append(get_default_env_path())
    return paths


def find_env_path() -> Optional[Path]:
    """查找第一个存在的 .env 文件路径。"""
    for p in get_env_paths():
        if p.exists():
            return p
    return None


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

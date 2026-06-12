"""
预下载 Argos Translate en-zh 翻译模型到项目目录
使用 argostranslate 内置包管理器，绕过 SSL 验证以适配国内网络。
"""

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
MODEL_DIR = PROJECT_DIR / "models" / "argos-translate"
PACKAGES_DIR = MODEL_DIR / "packages"
PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

os.environ["ARGOS_PACKAGES_DIR"] = str(PACKAGES_DIR)

import argostranslate.package
import argostranslate.settings
import requests
import warnings

argostranslate.settings.package_dir = str(PACKAGES_DIR)
warnings.filterwarnings("ignore")

# 全局 patch requests 跳过 SSL 验证（国内网络环境需要）
_orig_request = requests.Session.request
def _patched_request(self, method, url, **kwargs):
    kwargs["verify"] = False
    return _orig_request(self, method, url, **kwargs)
requests.Session.request = _patched_request


def _install_language_pair(from_code, to_code):
    """下载并安装指定语言对模型"""
    label = f"{from_code}->{to_code}"
    installed = argostranslate.package.get_installed_packages()
    found = next(
        (p for p in installed if p.from_code == from_code and p.to_code == to_code),
        None
    )
    if found:
        print(f"[OK] {label} 模型已安装 (路径: {found.package_path})")
        return True

    print(f"[..] 正在下载并安装 {label} 翻译模型...")
    try:
        ok = argostranslate.package.install_package_for_language_pair(from_code, to_code)
        if ok:
            print(f"[OK] {label} 模型下载安装成功!")
            return True
        else:
            print(f"[FAIL] {label} 安装失败，返回 False")
            return False
    except Exception as e:
        print(f"[FAIL] {label} 安装异常: {e}")
        return False


LANGUAGE_PAIRS = [
    ("en", "zh"),
    ("zh", "en"),
]


def verify():
    """简单翻译验证"""
    os.environ["ARGOS_CHUNK_TYPE"] = "MINISBD"
    import argostranslate.translate

    tests = [
        ("en", "zh", "Hello world", "en", "zh"),
        ("zh", "en", "你好世界", "zh", "en"),
    ]
    all_ok = True
    for from_code, to_code, text, label_f, label_t in tests:
        try:
            result = argostranslate.translate.translate(text, from_code, to_code)
            print(f"[OK] 翻译验证: '{text}' -> '{result}'")
        except Exception as e:
            print(f"[!] {label_f}->{label_t} 翻译验证失败: {e}")
            all_ok = False
    return all_ok


if __name__ == "__main__":
    print("=" * 50)
    print(" Argos Translate 翻译模型下载")
    print("=" * 50)
    print(f" 模型目录: {PACKAGES_DIR}")
    print()

    print("[..] 正在更新包索引...")
    try:
        argostranslate.package.update_package_index()
    except Exception as e:
        print(f"[!] 包索引更新警告: {e}")
    print()

    all_success = True
    for from_code, to_code in LANGUAGE_PAIRS:
        if not _install_language_pair(from_code, to_code):
            all_success = False
        print()

    if all_success:
        verify()
        print()
        print("全部完成! 可以启动 Streamlit 使用翻译功能。")
    else:
        print()
        print("部分模型下载失败。备选方案:")
        print(f"  1. 手动下载 .argosmodel 放入 {PACKAGES_DIR}")
        print("  2. 检查网络后重试")
        sys.exit(1)

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


def download_model():
    """通过 argostranslate 内置包管理器下载并安装 en-zh 模型"""
    installed = argostranslate.package.get_installed_packages()
    en_zh = next(
        (p for p in installed if p.from_code == "en" and p.to_code == "zh"),
        None
    )
    if en_zh:
        print(f"[OK] en-zh 模型已安装 (路径: {en_zh.package_path})")
        return True

    print("[..] 正在更新包索引...")
    try:
        argostranslate.package.update_package_index()
    except Exception as e:
        print(f"[!] 包索引更新警告: {e}")

    print("[..] 正在下载并安装 en-zh 翻译模型...")
    try:
        ok = argostranslate.package.install_package_for_language_pair("en", "zh")
        if ok:
            print("[OK] 模型下载安装成功!")
            return True
        else:
            print("[FAIL] 安装失败，返回 False")
            return False
    except Exception as e:
        print(f"[FAIL] 安装异常: {e}")
        return False


def verify():
    """简单翻译验证"""
    os.environ["ARGOS_CHUNK_TYPE"] = "MINISBD"
    import argostranslate.translate

    try:
        result = argostranslate.translate.translate("Hello world", "en", "zh")
        print(f"[OK] 翻译验证: 'Hello world' -> '{result}'")
        return True
    except Exception as e:
        print(f"[!] 翻译验证失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print(" Argos Translate en-zh 模型下载")
    print("=" * 50)
    print(f" 模型目录: {PACKAGES_DIR}")
    print()

    if download_model():
        print()
        verify()
        print()
        print("全部完成! 可以启动 Streamlit 使用英中翻译。")
    else:
        print()
        print("下载失败。备选方案:")
        print(f"  1. 手动下载 .argosmodel 放入 {PACKAGES_DIR}")
        print("  2. 检查网络后重试")
        sys.exit(1)

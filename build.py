#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — 打包横向收藏夹扩展为 Edge / Chrome 发行包。

两种包均为 Manifest V3，核心代码完全一致：
  - chrome 包：标准 MV3 清单
  - edge   包：在标准清单基础上追加 browser_specific_settings.edge（Edge 商店标识，Chrome 会忽略）

二者都可在 Edge 与 Chrome 中“加载已解压缩的扩展程序”使用。
用法：python build.py
"""
import json
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
BUILD = os.path.join(ROOT, "build")

# 需要打进发行包的文件（相对 ROOT）
INCLUDE = [
    "manifest.json",
    "bg.js",
    "popup.html", "popup.css", "popup.js",
    "icons/icon16.png", "icons/icon48.png", "icons/icon128.png",
]

VERSION = "7.2.0"


def read_manifest():
    with open(os.path.join(ROOT, "manifest.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def write_manifest_variant(folder, edge=False):
    m = read_manifest()
    if edge:
        m["browser_specific_settings"] = {
            "edge": {
                "vendor": "bjb",
                "protocol_handler": {}
            }
        }
    with open(os.path.join(folder, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")


def stage_variant(edge):
    """把 INCLUDE 文件复制到 build/<variant>/ 并写入对应清单，返回目录路径。"""
    variant = "edge" if edge else "chrome"
    dst = os.path.join(BUILD, variant)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)

    for rel in INCLUDE:
        if rel == "manifest.json":
            continue  # 单独写入（含变体差异）
        src = os.path.join(ROOT, rel)
        tgt = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        shutil.copy2(src, tgt)

    write_manifest_variant(dst, edge=edge)
    return dst


def zip_dir(src_dir, zip_path):
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(src_dir):
            for fn in files:
                full = os.path.join(dirpath, fn)
                arc = os.path.relpath(full, src_dir)
                z.write(full, arc)
    print("  ->", os.path.relpath(zip_path, ROOT),
          f"({os.path.getsize(zip_path)} bytes)")


def main():
    if os.path.isdir(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(DIST, exist_ok=True)

    print("Building Edge package...")
    edge_dir = stage_variant(True)
    zip_dir(edge_dir, os.path.join(DIST, f"horizontal-bookmarks-edge-v{VERSION}.zip"))

    print("Building Chrome package...")
    chrome_dir = stage_variant(False)
    zip_dir(chrome_dir, os.path.join(DIST, f"horizontal-bookmarks-chrome-v{VERSION}.zip"))

    # 清理临时 build 目录，保留 dist 成品
    shutil.rmtree(BUILD)
    print("Done. Output in:", os.path.relpath(DIST, ROOT))


if __name__ == "__main__":
    main()

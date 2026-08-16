#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish.py — 将本地扩展仓库发布到 GitHub（仅依赖标准库）。

从环境变量读取凭据（不落盘）：
  GITHUB_TOKEN   带 repo 权限的 Personal Access Token
  GITHUB_USER    GitHub 用户名
  GITHUB_REPO    目标仓库名（默认 horizontal-bookmarks）

流程：
  1. 提交本地改动（若未提交）
  2. 通过 GitHub API 创建公开仓库（已存在则跳过）
  3. git push 到 main
  4. 创建 Release（tag vX.Y.Z）并上传 dist/ 下的两个 zip 作为附件
"""
import os
import sys
import json
import shutil
import subprocess
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("GITHUB_USER", "")
REPO = os.environ.get("GITHUB_REPO") or "horizontal-bookmarks"
VERSION = "7.2.0"

if not TOKEN:
    print("缺少环境变量 GITHUB_TOKEN")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "publish-script",
    "X-GitHub-Api-Version": "2022-11-28",
}


def api(method, path, data=None, binary=False, extra=None):
    url = API + path
    body = None
    hdr = dict(HEADERS)
    if data is not None:
        if binary:
            body = data
            hdr["Content-Type"] = "application/zip"
        else:
            body = json.dumps(data).encode("utf-8")
            hdr["Content-Type"] = "application/json"
    if extra:
        hdr.update(extra)
    req = urllib.request.Request(url, data=body, headers=hdr, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw and not binary else raw)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("git", args, "失败:\n", r.stderr)
        sys.exit(1)
    return r


def main():
    global USER
    # 未提供用户名时，用 Token 查询当前登录用户
    if not USER:
        code, resp = api("GET", "/user")
        if code == 200 and isinstance(resp, dict) and resp.get("login"):
            USER = resp["login"]
            print("当前 GitHub 用户:", USER)
        else:
            print("✗ 无法从 Token 获取用户名:", code, resp)
            sys.exit(1)

    # 1. 提交
    git("config", "user.name", USER)
    git("config", "user.email", f"{USER}@users.noreply.github.com")
    st = git("status", "--porcelain", check=False)
    if st.stdout.strip():
        git("add", "-A")
        git("commit", "-m", f"Release v{VERSION}", check=False)
    else:
        print("没有新的改动需要提交。")

    # 2. 创建仓库（已存在则忽略）
    code, resp = api("POST", "/user/repos", {
        "name": REPO,
        "description": "横向收藏夹 · 仿360书签面板（Edge/Chrome MV3 扩展）",
        "public": True,
        "auto_init": False,
    })
    if code in (201, 200):
        print("✓ 仓库已创建:", resp.get("html_url"))
    elif code == 422:
        print("· 仓库已存在，继续推送。")
    else:
        print("✗ 创建仓库失败:", code, resp)
        sys.exit(1)

    # 3. push（确保有提交；若仓库为空且本地无提交则先建一个空提交）
    st2 = git("status", "--porcelain", check=False)
    if not st2.stdout.strip() and not git("log", "-1", check=False).returncode == 0:
        git("commit", "--allow-empty", "-m", f"init v{VERSION}")

    # 设置 remote（含 token）
    remote_url = f"https://{TOKEN}@github.com/{USER}/{REPO}.git"
    cur = git("remote", "get-url", "origin", check=False)
    if cur.returncode == 0:
        git("remote", "set-url", "origin", remote_url)
    else:
        git("remote", "add", "origin", remote_url)

    branch = git("rev-parse", "--abbrev-ref", "HEAD", check=False).stdout.strip() or "main"
    # 若本地默认是 master，重命名为 main 以契合 GitHub 默认
    if branch == "master":
        git("branch", "-M", "main", check=False)
        branch = "main"
    p = git("push", "-u", "origin", branch, check=False)
    if p.returncode != 0:
        print("✗ push 失败:\n", p.stderr)
        sys.exit(1)
    print(f"✓ 已推送至 main（仓库 {USER}/{REPO}）")

    # 4. 创建 Release 并上传附件
    code, resp = api("POST", f"/repos/{USER}/{REPO}/releases", {
        "tag_name": f"v{VERSION}",
        "name": f"v{VERSION}",
        "body": "横向收藏夹扩展 v%s：Edge / Chrome 双格式发行包。" % VERSION,
        "draft": False,
        "prerelease": False,
    })
    if code not in (201, 200):
        print("✗ 创建 Release 失败:", code, resp)
        sys.exit(1)
    rid = resp.get("id")
    print("✓ Release 已创建, id =", rid)

    dist = os.path.join(ROOT, "dist")
    for fn in os.listdir(dist):
        if not fn.endswith(".zip"):
            continue
        path = os.path.join(dist, fn)
        with open(path, "rb") as f:
            data = f.read()
        code, resp = api(
            "POST",
            f"/repos/{USER}/{REPO}/releases/{rid}/assets?name={fn}",
            data=data, binary=True,
        )
        if code in (201, 200):
            print("  ✓ 已上传附件:", fn)
        else:
            print("  ✗ 上传附件失败:", fn, code, resp)

    print("\n完成！仓库地址: https://github.com/%s/%s" % (USER, REPO))
    print("Release 地址: https://github.com/%s/%s/releases/tag/v%s" % (USER, REPO, VERSION))


if __name__ == "__main__":
    main()

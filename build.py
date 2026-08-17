#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — 打包横向收藏夹扩展为 Edge / Chrome 发行包（zip + crx3）。

两种变体均为 Manifest V3，核心代码完全一致：
  - chrome 包：标准 MV3 清单
  - edge   包：在标准清单基础上追加 browser_specific_settings.edge

输出格式：
  - *.zip    — 可解压后“加载已解压缩的扩展程序”
  - *.crx    — 可直接拖入浏览器安装（需开启开发者模式）

用法：python build.py
"""
import hashlib
import io
import json
import os
import shutil
import struct
import zipfile

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
BUILD = os.path.join(ROOT, "build")
KEY_FILE = os.path.join(ROOT, ".crx-key.pem")  # 签名密钥持久化（保持同一 extension ID）

INCLUDE = [
    "manifest.json",
    "bg.js",
    "popup.html", "popup.css", "popup.js",
    "icons/icon16.png", "icons/icon48.png", "icons/icon128.png",
]

VERSION = "7.2.0"


# ---------- 密钥管理 ----------
def get_or_create_key():
    """返回 RSA 私钥（首次自动生成并持久化到 .crx-key.pem）。"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(KEY_FILE, "wb") as f:
        f.write(pem)
    print("  已生成新密钥:", KEY_FILE)
    return key


def get_crx_id(public_key_bytes):
    """CRX ID = base16(sha256(pubkey)[:16])"""
    raw = hashlib.sha256(public_key_bytes).digest()[:16]
    return raw.hex()


def make_crx3(zip_data, private_key):
    """
    将 zip 字节签名为 CRX3 格式，返回完整 crx 字节。

    官方规范（chromium/src/components/crx_file/crx3.proto）：

    CrxFileHeader:
      field  2: repeated AsymmetricKeyProof sha256_with_rsa   { public_key, signature }
      field  3: repeated AsymmetricKeyProof sha256_with_ecdsa  { public_key, signature }
      field  4: optional bytes verified_contents
      field 10000: optional bytes signed_header_data           ← 序列化的 SignedData

    AsymmetricKeyProof:
      field 1: bytes public_key
      field 2: bytes signature

    SignedData:
      field 1: bytes crx_id   (恰好 16 字节)

    签名覆盖范围：
      "CRX3 SignedData\x00" + uint32_le(signed_header_len) + signed_header_data + zip
    """
    pub_der = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    crx_id_raw = hashlib.sha256(pub_der).digest()[:16]

    # ---- Protobuf 编码工具 ----
    def _varint(n):
        buf = bytearray()
        while True:
            b = n & 0x7F
            n >>= 7
            if n:
                buf.append(b | 0x80)
            else:
                buf.append(b)
                break
        return bytes(buf)

    def _field(field_num, raw_bytes):
        """Encode a length-delimited (wire type 2) field."""
        return _varint((field_num << 3) | 2) + _varint(len(raw_bytes)) + raw_bytes

    # ---- 1. 构建 SignedData { crx_id } → 得到 signed_header_data ----
    signed_header_data = _field(1, crx_id_raw)

    # ---- 2. 计算签名（RSA-SHA256，覆盖 signed_header + zip）----
    sign_payload = (
        b"CRX3 SignedData\x00"
        + struct.pack("<I", len(signed_header_data))
        + signed_header_data
        + zip_data
    )
    signature = private_key.sign(
        sign_payload,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    # ---- 3. 构建 AsymmetricKeyProof { public_key, signature } ----
    proof = bytearray()
    proof += _field(1, pub_der)       # public_key
    proof += _field(2, signature)     # signature
    proof_bytes = bytes(proof)

    # ---- 4. 构建外层 CrxFileHeader ----
    header = bytearray()
    header += _field(2, proof_bytes)              # sha256_with_rsa (field 2)
    header += _field(10000, signed_header_data)   # signed_header_data (field 10000)
    header_bytes = bytes(header)

    # ---- 5. 拼装完整 CRX3 文件 ----
    crx = bytearray()
    crx += b"Cr24"                          # magic
    crx += struct.pack("<I", 3)              # version = 3
    crx += struct.pack("<I", len(header_bytes))  # header size
    crx += header_bytes                      # CrxFileHeader protobuf
    crx += zip_data                           # ZIP archive
    return bytes(crx)


# ---------- 清单与文件复制 ----------
def read_manifest():
    with open(os.path.join(ROOT, "manifest.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def write_manifest_variant(folder, edge=False):
    m = read_manifest()
    if edge:
        m["browser_specific_settings"] = {
            "edge": {"vendor": "bjb", "protocol_handler": {}}
        }
    with open(os.path.join(folder, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")


def stage_variant(edge):
    variant = "edge" if edge else "chrome"
    dst = os.path.join(BUILD, variant)
    if os.path.isdir(dst):
        try:
            shutil.rmtree(dst)
        except OSError:
            pass
    os.makedirs(dst, exist_ok=True)
    for rel in INCLUDE:
        if rel == "manifest.json":
            continue
        src = os.path.join(ROOT, rel)
        tgt = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        shutil.copy2(src, tgt)
    write_manifest_variant(dst, edge=edge)
    return dst


def zip_dir_to_bytes(src_dir):
    """将目录打包为 zip 并返回字节。"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(src_dir):
            for fn in files:
                full = os.path.join(dirpath, fn)
                arc = os.path.relpath(full, src_dir)
                z.write(full, arc)
    return buf.getvalue()


def write_file(path, data):
    with open(path, "wb") as f:
        f.write(data)
    print("  ->", os.path.relpath(path, ROOT), f"({len(data)} bytes)")


# ---------- 主流程 ----------
def main():
    if os.path.isdir(BUILD):
        try:
            shutil.rmtree(BUILD)
        except OSError:
            pass  # 安全删除拦截时跳过，后续复制会覆盖旧文件
    os.makedirs(DIST, exist_ok=True)

    private_key = get_or_create_key()
    pub_der = private_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    ext_id = get_crx_id(pub_der)
    print("Extension ID:", ext_id)

    for edge in [True, False]:
        label = "Edge" if edge else "Chrome"
        print(f"\nBuilding {label} package...")
        src_dir = stage_variant(edge)

        # ZIP
        zip_data = zip_dir_to_bytes(src_dir)
        name = f"horizontal-bookmarks-{'edge' if edge else 'chrome'}-v{VERSION}"
        write_file(os.path.join(DIST, f"{name}.zip"), zip_data)

        # CRX3
        crx_data = make_crx3(zip_data, private_key)
        write_file(os.path.join(DIST, f"{name}.crx"), crx_data)

    try:
        shutil.rmtree(BUILD)
    except OSError:
        pass
    print("\nDone. Output in:", os.path.relpath(DIST, ROOT))


if __name__ == "__main__":
    main()

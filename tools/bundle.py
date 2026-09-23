#!/usr/bin/env python3
"""
tools/bundle.py

Kenapa perlu ini:
Azure Load Balancer kerja per KONEKSI TCP, bukan per halaman/domain. Kalau
index.html masih minta file terpisah (style.css, script.js, foto.jpg,
logo/*, proyek/*), tiap request itu koneksi baru yang bisa "nyasar" ke VM
lain (punya orang lain), jadi styling/foto bisa ilang atau ketuker pas
refresh.

Script ini nge-gabungin semuanya jadi SATU file HTML mandiri:
- style.css        -> di-inline jadi <style>...</style>
- script.js        -> di-inline jadi <script>...</script>
- foto.jpg,
  logo/*.svg|png,
  proyek/*.jpg      -> di-inline jadi base64 data URI di atribut src=

Google Fonts (fonts.googleapis.com) SENGAJA dibiarin eksternal — itu
domain pihak ketiga yang sama buat semua VM, bukan salah satu VM kalian,
jadi nggak kena masalah LB affinity ini.

Input : index.html + style.css + script.js + foto.jpg + logo/ + proyek/
        (dibaca dari root repo)
Output: dist/index.html  (satu file, siap di-COPY ke image nginx)

Jalanin dari root repo:
    python3 tools/bundle.py
"""

import re
import base64
import mimetypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_HTML = ROOT / "index.html"
OUT_DIR = ROOT / "dist"
OUT_HTML = OUT_DIR / "index.html"


def to_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "application/octet-stream"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def inline_css(html: str) -> str:
    pattern = r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\':]+\.css)["\'][^>]*>'

    def repl(match):
        href = match.group(1)
        css_path = ROOT / href
        if not css_path.exists():
            print(f"  [skip] CSS tidak ditemukan, dilewati: {href}")
            return match.group(0)
        css = css_path.read_text(encoding="utf-8")
        print(f"  [inline css] {href} ({len(css)} bytes)")
        return f"<style>\n{css}\n</style>"

    return re.sub(pattern, repl, html)


def inline_js(html: str) -> str:
    pattern = r'<script[^>]+src=["\']([^"\':]+\.js)["\'][^>]*></script>'

    def repl(match):
        src = match.group(1)
        js_path = ROOT / src
        if not js_path.exists():
            print(f"  [skip] JS tidak ditemukan, dilewati: {src}")
            return match.group(0)
        js = js_path.read_text(encoding="utf-8")
        print(f"  [inline js] {src} ({len(js)} bytes)")
        return f"<script>\n{js}\n</script>"

    return re.sub(pattern, repl, html)


def inline_images(html: str) -> str:
    # src="foto.jpg" / src="logo/azure.svg" / src="proyek/proyek-1.jpg" dst.
    # Dilewatin kalau sudah http(s):// atau data: (misal favicon SVG yang
    # sudah inline dari sononya).
    pattern = r'(src)=(["\'])([^"\']+\.(?:jpg|jpeg|png|svg|gif|webp))\2'

    def repl(match):
        attr, quote, src = match.group(1), match.group(2), match.group(3)
        img_path = ROOT / src
        if not img_path.exists():
            print(f"  [skip] Gambar tidak ditemukan, dilewati: {src}")
            return match.group(0)
        uri = to_data_uri(img_path)
        print(f"  [inline img] {src} ({img_path.stat().st_size} bytes)")
        return f"{attr}={quote}{uri}{quote}"

    return re.sub(pattern, repl, html)


def main():
    if not SRC_HTML.exists():
        raise SystemExit(f"index.html tidak ketemu di {SRC_HTML}")

    html = SRC_HTML.read_text(encoding="utf-8")

    print("Inlining CSS...")
    html = inline_css(html)
    print("Inlining JS...")
    html = inline_js(html)
    print("Inlining gambar (foto.jpg, logo/*, proyek/*)...")
    html = inline_images(html)

    OUT_DIR.mkdir(exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    size_kb = OUT_HTML.stat().st_size / 1024
    print(f"\nSelesai -> {OUT_HTML} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()

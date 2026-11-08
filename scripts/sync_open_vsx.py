#!/usr/bin/env python3
"""Synchronize compact, self-contained SVG extension cards for the GitHub profile.

GitHub READMEs strip arbitrary CSS. Each card is a standalone styled SVG image,
linked to Open VSX. Only the designated README segment and generated SVG files
are modified. No dependencies outside the Python standard library.
"""
from __future__ import annotations

import base64
import html
import json
import re
import textwrap
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

NAMESPACE = "armotusitio"
CATALOG_URL = f"https://open-vsx.org/api/{NAMESPACE}"
ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CARDS_DIR = ROOT / "assets" / "open-vsx"
START = "<!-- OPEN_VSX_EXTENSIONS:START -->"
END = "<!-- OPEN_VSX_EXTENSIONS:END -->"
PREFERRED_ORDER = ("orquestivo", "probato-pr", "indizivo", "saturivo")
COLUMNS = 3
MAX_ICON_BYTES = 256 * 1024
ACCENTS = {"orquestivo": "#7A9CFF", "probato-pr": "#63FF8A", "indizivo": "#42D6C5", "saturivo": "#F0B76B"}
# Publisher-owned, official Marketplace icon paths, confirmed against each extension package.json.
OFFICIAL_ICONS = {
    "orquestivo": "https://raw.githubusercontent.com/Drako01/orquestivo/main/media/icon-128.png",
    "probato-pr": "https://raw.githubusercontent.com/Drako01/probato-pr/main/media/logo.png",
    "indizivo": "https://raw.githubusercontent.com/Drako01/indizivo/main/media/indizivo-icon-128.png",
    "saturivo": "https://raw.githubusercontent.com/Drako01/saturivo/main/media/saturivo-icon.png",
}



def get_json(url: str) -> dict:
    request = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Drako01-profile-gallery/2.0",
    })
    with urlopen(request, timeout=20) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected response from {url}")
    return data


def safe_icon(url: object) -> str:
    """Accept only icon URLs under the Open VSX HTTPS origin."""
    if not isinstance(url, str):
        return ""
    parsed = urlparse(url)
    return url if (
        parsed.scheme == "https" and parsed.hostname == "open-vsx.org"
        and parsed.port in (None, 443) and parsed.username is None and parsed.password is None
    ) else ""


def get_icon_data(url: str) -> str:
    """Embed the actual PNG/JPEG/WebP icon. Never substitute a made-up brand mark."""
    parsed = urlparse(url)
    allowed = safe_icon(url) or url in OFFICIAL_ICONS.values()
    if not allowed or parsed.scheme != "https":
        raise ValueError(f"Icon URL is not approved: {url}")

    request = Request(url, headers={"User-Agent": "Drako01-profile-gallery/2.0"})
    with urlopen(request, timeout=20) as response:
        data = response.read(MAX_ICON_BYTES + 1)
        final_url = urlparse(response.geturl())
        if final_url.hostname not in ("open-vsx.org", "raw.githubusercontent.com") or len(data) > MAX_ICON_BYTES:
            raise ValueError(f"Untrusted or oversized icon: {url}")
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            mime = "image/png"
        elif data.startswith(b"\xff\xd8\xff"):
            mime = "image/jpeg"
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            mime = "image/webp"
        else:
            raise ValueError(f"Unsupported icon format: {url}")
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def collect_extensions(fetch=get_json) -> list[dict]:
    namespace = fetch(CATALOG_URL)
    names = namespace.get("extensions")
    if namespace.get("name", "").lower() != NAMESPACE or not isinstance(names, dict) or not names:
        raise ValueError("Open VSX namespace missing or empty; README left unchanged")

    result = []
    for slug in names:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", slug):
            raise ValueError(f"Invalid extension name: {slug!r}")
        data = fetch(f"{CATALOG_URL}/{quote(slug)}/latest")
        if data.get("reviewStatus") not in (None, "published") or data.get("preRelease") is True:
            continue
        if data.get("namespace") != NAMESPACE or data.get("name") != slug:
            raise ValueError(f"Invalid metadata: {slug}")

        display_name = data.get("displayName") or slug.replace("-", " ").title()
        if not isinstance(display_name, str) or (display_name.startswith("%") and display_name.endswith("%")):
            display_name = slug.replace("-", " ").title()
        version = data.get("version")
        count = data.get("downloadCount")
        if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+-]*", version):
            raise ValueError(f"Invalid version for {slug}")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"Invalid downloads for {slug}")
        files = data.get("files") or {}
        result.append({
            "slug": slug,
            "name": display_name,
            "description": data.get("description") if isinstance(data.get("description"), str) else "Developer productivity tools.",
            "version": version,
            "downloads": count,
            "icon": safe_icon(files.get("icon")) if isinstance(files, dict) else "",
        })

    if not result:
        raise ValueError("No published Open VSX extensions; README left unchanged")
    return sorted(result, key=lambda e: (
        PREFERRED_ORDER.index(e["slug"]) if e["slug"] in PREFERRED_ORDER else len(PREFERRED_ORDER),
        e["slug"],
    ))


def clipped(text: object, limit: int) -> str:
    normalized = " ".join(str(text).split())
    return normalized if len(normalized) <= limit else normalized[: limit - 1].rstrip() + "…"


def render_card(item: dict, icon_data: str = "") -> str:
    """Render a fully styled, static card that GitHub can show without HTML/CSS support."""
    slug = item["slug"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", slug):
        raise ValueError("Unsafe filename")
    accent = ACCENTS.get(slug, "#63FF8A")
    name = html.escape(clipped(item["name"], 20), quote=False)
    version = html.escape(clipped(item["version"], 20), quote=False)
    desc = clipped(item["description"], 91)
    description = textwrap.wrap(desc, width=32, break_long_words=False, break_on_hyphens=False)[:3]
    lines = "\n".join(
        f'  <text x="19" y="{140 + i * 19}" fill="#B9C9D6" font-size="13" font-weight="400">{html.escape(line, quote=False)}</text>'
        for i, line in enumerate(description)
    )
    if not icon_data.startswith(("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/webp;base64,")):
        raise ValueError(f"Real published icon is required: {slug}")
    icon = f'<image x="19" y="21" width="62" height="62" preserveAspectRatio="xMidYMid meet" href="{html.escape(icon_data, quote=True)}"/>'
    downloads = f'{int(item["downloads"]):,}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="252" height="254" viewBox="0 0 252 254" role="img" aria-label="{html.escape(str(item["name"]), quote=True)}, version {version}, {downloads} downloads">
<defs>
  <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#162431"/><stop offset="100%" stop-color="#0C131E"/></linearGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="{accent}"/><stop offset="100%" stop-color="#63FF8A"/></linearGradient>
  <radialGradient id="light"><stop offset="0%" stop-color="{accent}" stop-opacity=".17"/><stop offset="100%" stop-color="{accent}" stop-opacity="0"/></radialGradient>
</defs>
<rect x="1.5" y="1.5" width="249" height="251" rx="16" fill="url(#surface)" stroke="#344654" stroke-width="1.5"/>
<rect x="2" y="2" width="248" height="2.5" rx="1.25" fill="url(#accent)"/>
<circle cx="224" cy="19" r="95" fill="url(#light)"/>
<rect x="14" y="16" width="72" height="72" rx="13" fill="#10202B" stroke="#2D4351"/>
{icon}
<text x="100" y="33" fill="{accent}" font-size="9.5" font-family="Segoe UI, Arial, sans-serif" font-weight="700" letter-spacing="1.1">VS CODE TOOL</text>
<text x="100" y="57" fill="#F2F6FA" font-size="17" font-family="Segoe UI, Arial, sans-serif" font-weight="700">{name}</text>
<text x="100" y="73" fill="#819BAA" font-size="11" font-family="Segoe UI, Arial, sans-serif">armotusitio</text>
<path d="M17 103H235" stroke="#2C3D4B"/>
<g font-family="Segoe UI, Arial, sans-serif">
  <text x="18" y="116" fill="#748C9E" font-size="9" font-weight="700" letter-spacing="1.2">WHAT IT DOES</text>
{lines}
  <path d="M17 198H235" stroke="#2C3D4B"/>
  <text x="19" y="217" fill="#748C9E" font-size="10" font-weight="600">VERSION</text>
  <text x="233" y="217" fill="#748C9E" font-size="10" text-anchor="end" font-weight="600">DOWNLOADS</text>
  <rect x="16" y="223" width="91" height="23" rx="7" fill="#21362E" stroke="#356E52"/>
  <text x="61" y="239" fill="#8FFBB0" text-anchor="middle" font-size="12" font-weight="700">v{version}</text>
  <text x="233" y="240" fill="#E9F2F9" text-anchor="end" font-size="16" font-weight="700">{downloads}</text>
</g>
</svg>'''


def render_gallery(extensions: list[dict]) -> str:
    if not extensions:
        raise ValueError("Refusing to replace a gallery with an empty result")
    rows = []
    for start in range(0, len(extensions), COLUMNS):
        items = extensions[start : start + COLUMNS]
        cells = ['<p align="center">']
        for index, item in enumerate(items):
            slug = item["slug"]
            url = f"https://open-vsx.org/extension/{NAMESPACE}/{quote(slug)}"
            title = html.escape(str(item["name"]), quote=True)
            if index:
                cells.append("  &emsp;")
            cells.append(
                f'  <a href="{url}"><img src="assets/open-vsx/{slug}.svg" width="29%" '
                f'alt="{title} — v{html.escape(str(item["version"]), quote=True)}; '
                f'{item["downloads"]:,} downloads" /></a>'
            )
        cells.append("</p>")
        rows.append("\n".join(cells))
    return "\n\n".join(rows)


def replace_gallery(readme: str, gallery: str) -> str:
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("Expected exactly one pair of gallery markers")
    before, rest = readme.split(START, 1)
    _, after = rest.split(END, 1)
    return f"{before}{START}\n{gallery}\n{END}{after}"


def main() -> None:
    extensions = collect_extensions()
    current = README.read_text(encoding="utf-8")
    updated = replace_gallery(current, render_gallery(extensions))
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    # Prepare all outputs first. Do not touch the README if the catalog is unavailable.
    cards = {
        CARDS_DIR / f'{item["slug"]}.svg': render_card(
            item, get_icon_data(OFFICIAL_ICONS.get(item["slug"]) or item["icon"])
        )
        for item in extensions
    }
    changes = 0
    for path, svg in cards.items():
        if not path.exists() or path.read_text(encoding="utf-8") != svg:
            path.write_text(svg, encoding="utf-8")
            changes += 1
    if updated != current:
        README.write_text(updated, encoding="utf-8")
        changes += 1
    print(f"Open VSX: {len(extensions)} extensions, {changes} changed files")
    for item in extensions:
        print(f"  {item['slug']} v{item['version']} — {item['downloads']:,} downloads")


if __name__ == "__main__":
    main()

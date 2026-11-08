#!/usr/bin/env python3
"""Synchronize the Open VSX extension gallery in the GitHub profile README.

Only the content between OPEN_VSX_EXTENSIONS markers is changed.
No third-party dependencies or credentials are required.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

NAMESPACE = "armotusitio"
CATALOG_URL = f"https://open-vsx.org/api/{NAMESPACE}"
README = Path(__file__).resolve().parents[1] / "README.md"
START = "<!-- OPEN_VSX_EXTENSIONS:START -->"
END = "<!-- OPEN_VSX_EXTENSIONS:END -->"
PREFERRED_ORDER = ("orquestivo", "probato-pr", "indizivo", "saturivo")
COLUMNS = 4


def get_json(url: str) -> dict:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "Drako01-profile-gallery/1.0"},
    )
    with urlopen(request, timeout=20) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError(f"Unexpected API response from {url}")
    return value


def safe_icon(url: object) -> str:
    """Use only HTTPS icons provided by the trusted Open VSX API."""
    if not isinstance(url, str):
        return ""
    parsed = urlparse(url)
    return url if parsed.scheme == "https" and parsed.hostname == "open-vsx.org" else ""


def collect_extensions(fetch=get_json) -> list[dict]:
    namespace = fetch(CATALOG_URL)
    names = namespace.get("extensions")
    if namespace.get("name", "").lower() != NAMESPACE or not isinstance(names, dict) or not names:
        raise ValueError("Open VSX namespace is missing or has no extensions; README unchanged")

    extensions = []
    for slug in names:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", slug):
            raise ValueError(f"Invalid Open VSX extension name: {slug!r}")
        metadata = fetch(f"{CATALOG_URL}/{quote(slug)}/latest")
        if metadata.get("reviewStatus") not in (None, "published") or metadata.get("preRelease") is True:
            continue
        if metadata.get("namespace") != NAMESPACE or metadata.get("name") != slug:
            raise ValueError(f"Invalid metadata for {slug}")

        display_name = metadata.get("displayName") or slug.replace("-", " ").title()
        if display_name.startswith("%") and display_name.endswith("%"):
            display_name = slug.replace("-", " ").title()
        version = metadata.get("version")
        if not isinstance(version, str) or not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z.+-]*", version):
            raise ValueError(f"Invalid version for {slug}")
        files = metadata.get("files") or {}
        icon = safe_icon(files.get("icon")) if isinstance(files, dict) else ""
        extensions.append({
            "slug": slug,
            "name": display_name,
            "description": metadata.get("description") or "VS Code extension published on Open VSX",
            "version": version,
            "icon": icon,
        })

    if not extensions:
        raise ValueError("No published Open VSX extensions returned; README unchanged")
    return sorted(extensions, key=lambda e: (
        PREFERRED_ORDER.index(e["slug"]) if e["slug"] in PREFERRED_ORDER else len(PREFERRED_ORDER),
        e["slug"],
    ))


def clipped(value: object, limit: int = 78) -> str:
    plain = " ".join(str(value).split())
    return plain if len(plain) <= limit else plain[: limit - 1].rstrip() + "…"


def render_gallery(extensions: list[dict]) -> str:
    if not extensions:
        raise ValueError("Refusing to render an empty gallery")
    rows = ["<table>", "  <tbody>"]
    for offset in range(0, len(extensions), COLUMNS):
        rows.append("    <tr>")
        for item in extensions[offset: offset + COLUMNS]:
            url = f"https://open-vsx.org/extension/{NAMESPACE}/{quote(item['slug'])}"
            title = html.escape(str(item["name"]), quote=True)
            description = html.escape(clipped(item["description"]), quote=True)
            version = html.escape(str(item["version"]), quote=True)
            icon = safe_icon(item.get("icon"))
            image = (
                f'<img src="{html.escape(icon, quote=True)}" width="58" height="58" alt="{title} icon" />'
                if icon else '<strong>🧩</strong>'
            )
            rows.extend([
                '      <td width="25%" align="center" valign="top">',
                f'        <a href="{url}">{image}</a>',
                f'        <p><strong><a href="{url}">{title}</a></strong></p>',
                f'        <sub>{description}</sub>',
                f'        <p><code>v{version}</code> · <a href="{url}">Open VSX</a></p>',
                "      </td>",
            ])
        for _ in range(COLUMNS - len(extensions[offset: offset + COLUMNS])):
            rows.append('      <td width="25%"></td>')
        rows.append("    </tr>")
    rows.extend(["  </tbody>", "</table>"])
    return "\n".join(rows)


def replace_gallery(readme: str, gallery: str) -> str:
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("Expected exactly one pair of Open VSX gallery markers")
    before, rest = readme.split(START, 1)
    _, after = rest.split(END, 1)
    return f"{before}{START}\n{gallery}\n{END}{after}"


def main() -> None:
    extensions = collect_extensions()
    current = README.read_text(encoding="utf-8")
    updated = replace_gallery(current, render_gallery(extensions))
    if updated != current:
        README.write_text(updated, encoding="utf-8")
        print(f"Updated profile gallery: {len(extensions)} extensions")
    else:
        print(f"Gallery already current: {len(extensions)} extensions")


if __name__ == "__main__":
    main()

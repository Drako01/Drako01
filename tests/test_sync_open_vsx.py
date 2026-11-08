"""Offline tests for the Open VSX PNG gallery and safe README updates."""
import base64
import unittest

from cairosvg import svg2png
from xml.etree import ElementTree

from scripts.sync_open_vsx import (
    CATALOG_URL,
    START,
    END,
    collect_extensions,
    render_card,
    render_gallery,
    replace_gallery,
    safe_icon,
    OFFICIAL_ICONS,
)


def metadata(slug, version="1.2.3", downloads=1234):
    return {
        "namespace": "armotusitio",
        "name": slug,
        "displayName": slug.title(),
        "description": "Reliable diagnostics for developers.",
        "version": version,
        "downloadCount": downloads,
        "reviewStatus": "published",
        "preRelease": False,
        "files": {"icon": f"https://open-vsx.org/api/armotusitio/{slug}/{version}/file/icon.png"},
    }


class GalleryTest(unittest.TestCase):
    def test_collects_every_extension_and_adds_new_extensions(self):
        slugs = ["saturivo", "indizivo", "orquestivo", "probato-pr", "noditrivo"]

        def fake_fetch(url):
            if url == CATALOG_URL:
                return {"name": "armotusitio", "extensions": {slug: url + "/" + slug for slug in slugs}}
            return metadata(url.split("/")[-2])

        items = collect_extensions(fake_fetch)
        self.assertEqual([item["slug"] for item in items], [
            "orquestivo", "probato-pr", "indizivo", "saturivo", "noditrivo"
        ])
        gallery = render_gallery(items)
        self.assertEqual(gallery.count('<p align="center">'), 2)
        self.assertEqual(gallery.count('width="29%"'), 5)
        self.assertEqual(gallery.count("&emsp;"), 3)
        rows = gallery.split('<p align="center">')[1:]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].count('<img '), 3)
        self.assertEqual(rows[1].count('<img '), 2)
        self.assertIn("https://open-vsx.org/extension/armotusitio/noditrivo", gallery)
        self.assertIn("1,234 downloads", gallery)
        self.assertIn("assets/open-vsx/noditrivo.png", gallery)

    def test_card_is_svg_with_background_rounded_border_version_and_downloads(self):
        item = {
            "slug": "indizivo",
            "name": "Indizivo",
            "description": "Reproducible development environment diagnostics.",
            "version": "0.2.2",
            "downloads": 1720,
        }
        svg = render_card(item, "data:image/png;base64,AA==")
        root = ElementTree.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn('rx="16"', svg)
        self.assertIn("url(#surface)", svg)
        self.assertIn("v0.2.2", svg)
        self.assertIn("1,720", svg)
        self.assertIn("Indizivo", svg)
        self.assertIn('y="154"', svg)
        self.assertIn('M17 221H235', svg)
        # The WHAT IT DOES label is at y=116, description starts at y=154.
        self.assertGreaterEqual(154 - 116, 38)

    def test_card_is_rasterized_to_png_with_embedded_logo(self):
        icon_png = svg2png(bytestring=(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2">'
            b'<rect width="2" height="2" fill="#21c985"/></svg>'
        ))
        icon = "data:image/png;base64," + base64.b64encode(icon_png).decode("ascii")
        item = {
            "slug": "noditrivo", "name": "Noditrivo",
            "description": "Change impact intelligence", "version": "0.1.0", "downloads": 52,
        }
        svg = render_card(item, icon)
        self.assertIn(icon, svg)
        card_png = svg2png(bytestring=svg.encode("utf-8"), output_width=756, output_height=852)
        self.assertTrue(card_png.startswith(b"\\x89PNG\\r\\n\\x1a\\n"))
        self.assertGreater(len(card_png), 1000)

    def test_replaces_only_delimited_gallery(self):
        readme = f"Before\n{START}\nOLD\n{END}\nAfter\n"
        self.assertEqual(
            replace_gallery(readme, "<p>gallery</p>"),
            f"Before\n{START}\n<p>gallery</p>\n{END}\nAfter\n",
        )

    def test_refuses_missing_markers_or_empty_namespace(self):
        with self.assertRaises(ValueError):
            replace_gallery("Other text", "<p>gallery</p>")
        with self.assertRaises(ValueError):
            render_gallery([])
        with self.assertRaises(ValueError):
            collect_extensions(lambda _: {"name": "armotusitio", "extensions": {}})

    def test_escape_metadata_and_reject_external_icons(self):
        malicious_name = '<img src=x onerror=alert(1)>'
        malicious_description = '<script>alert("x")</script>'
        item = {
            "slug": "example",
            "name": malicious_name,
            "description": malicious_description,
            "version": "1.2.3",
            "downloads": 100,
            "icon": safe_icon("https://example.com/icon.svg"),
        }
        svg = render_card(item, "data:image/png;base64,AA==")
        ElementTree.fromstring(svg)
        self.assertNotIn('<script>', svg)
        self.assertNotIn(malicious_name, svg)
        self.assertIn('&lt;script&gt;', svg)
        self.assertNotIn("example.com", svg)

    def test_requires_real_brand_logo_and_references_official_sources(self):
        for slug in ("orquestivo", "probato-pr", "indizivo", "saturivo"):
            self.assertIn(slug, OFFICIAL_ICONS)
            self.assertTrue(OFFICIAL_ICONS[slug].startswith("https://raw.githubusercontent.com/Drako01/"))
        item = {
            "slug": "noditrivo", "name": "Noditrivo", "description": "Change impact analysis",
            "version": "0.1.0", "downloads": 50,
        }
        with self.assertRaisesRegex(ValueError, "Real published icon is required"):
            render_card(item)
        self.assertIn('href="data:image/png;base64,AA=="', render_card(item, "data:image/png;base64,AA=="))

    def test_rejects_missing_download_count(self):
        def fake_fetch(url):
            if url == CATALOG_URL:
                return {"name": "armotusitio", "extensions": {"example": "url"}}
            data = metadata("example")
            del data["downloadCount"]
            return data

        with self.assertRaises(ValueError):
            collect_extensions(fake_fetch)


if __name__ == "__main__":
    unittest.main()

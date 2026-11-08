"""Offline tests for the Open VSX SVG gallery and safe README updates."""
import unittest
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
        self.assertEqual(gallery.count('width="23.5%"'), 5)
        self.assertIn("https://open-vsx.org/extension/armotusitio/noditrivo", gallery)
        self.assertIn("1,234 downloads", gallery)
        self.assertIn("assets/open-vsx/noditrivo.svg", gallery)

    def test_card_is_svg_with_background_rounded_border_version_and_downloads(self):
        item = {
            "slug": "indizivo",
            "name": "Indizivo",
            "description": "Reproducible development environment diagnostics.",
            "version": "0.2.2",
            "downloads": 1720,
        }
        svg = render_card(item)
        root = ElementTree.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn('rx="16"', svg)
        self.assertIn("url(#surface)", svg)
        self.assertIn("v0.2.2", svg)
        self.assertIn("1,720", svg)
        self.assertIn("Indizivo", svg)

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
        svg = render_card(item)
        ElementTree.fromstring(svg)
        self.assertNotIn('<script>', svg)
        self.assertNotIn(malicious_name, svg)
        self.assertIn('&lt;script&gt;', svg)
        self.assertNotIn("example.com", svg)

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

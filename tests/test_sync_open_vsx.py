"""Offline contract tests for the Open VSX profile gallery."""
import unittest

from scripts.sync_open_vsx import (
    CATALOG_URL,
    START,
    END,
    collect_extensions,
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
            slug = url.split("/")[-2]
            return metadata(slug)

        items = collect_extensions(fake_fetch)
        self.assertEqual([item["slug"] for item in items], [
            "orquestivo", "probato-pr", "indizivo", "saturivo", "noditrivo"
        ])
        gallery = render_gallery(items)
        self.assertEqual(gallery.count("<tr>"), 2)
        self.assertEqual(gallery.count('<td width="25%"'), 8)
        self.assertIn("https://open-vsx.org/extension/armotusitio/noditrivo", gallery)
        self.assertIn("1,234 downloads", gallery)
        self.assertIn("<code>v1.2.3</code>", gallery)

    def test_replaces_only_delimited_gallery(self):
        readme = f"Before\n{START}\nOLD\n{END}\nAfter\n"
        result = replace_gallery(readme, "<table></table>")
        self.assertEqual(result, f"Before\n{START}\n<table></table>\n{END}\nAfter\n")

    def test_refuses_missing_markers_and_empty_catalog(self):
        with self.assertRaises(ValueError):
            replace_gallery("Other text", "<table></table>")
        with self.assertRaises(ValueError):
            render_gallery([])
        with self.assertRaises(ValueError):
            collect_extensions(lambda _: {"name": "armotusitio", "extensions": {}})

    def test_escapes_untrusted_metadata_and_rejects_external_icons(self):
        raw_name = '<img src=x onerror=alert(1)>'
        raw_description = '<script>alert("x")</script>'
        rendered = render_gallery([{
            "slug": "example",
            "name": raw_name,
            "description": raw_description,
            "version": "1.2.3",
            "downloads": 100,
            "icon": safe_icon("https://example.com/icon.svg"),
        }])
        self.assertNotIn("<script>", rendered)
        self.assertNotIn('<img src=x onerror=alert(1)>', rendered)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', rendered)
        self.assertNotIn("example.com", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_fails_closed_if_download_count_missing(self):
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

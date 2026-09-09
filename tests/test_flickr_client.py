import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from flickr_client import FlickrClient, Photo


LICENSES = {
    "licenses": {
        "license": [
            {"id": 0, "name": "All Rights Reserved", "url": ""},
            {"id": 4, "name": "CC BY 2.0", "url": "https://license/4"},
            {
                "id": 7,
                "name": "No known copyright restrictions",
                "url": "https://license/7",
            },
        ]
    }
}


class FlickrClientTests(unittest.TestCase):
    def make_client(self):
        with patch("flickr_client.FlickrAPI") as api:
            client = FlickrClient("key", "secret")
            client.flickr = api.return_value
        client.flickr.photos.licenses.getInfo.return_value = LICENSES
        return client

    def test_search_requests_allowed_licenses_and_filters_blocked_results(self):
        client = self.make_client()
        client.flickr.photos.search.return_value = {
            "photos": {
                "photo": [
                    {
                        "id": "1",
                        "owner": "a",
                        "title": "blocked",
                        "license": "0",
                        "url_o": "https://image/1",
                    },
                    {
                        "id": "2",
                        "owner": "b",
                        "ownername": "Bee",
                        "title": "allowed",
                        "license": "4",
                        "url_o": "https://image/2",
                    },
                ]
            }
        }

        photos = client.search_photos("cats", 2)

        self.assertEqual([photo.id for photo in photos], ["2"])
        self.assertIsNotNone(photos[0].warning)
        requested = client.flickr.photos.search.call_args.kwargs["license"].split(",")
        self.assertTrue({"0", "3", "6", "16"}.isdisjoint(requested))

    def test_unrestricted_license_has_no_warning(self):
        client = self.make_client()
        client.flickr.photos.search.return_value = {
            "photos": {
                "photo": [
                    {
                        "id": "2",
                        "owner": "b",
                        "title": "allowed",
                        "license": "7",
                        "url_o": "https://image/2",
                    }
                ]
            }
        }

        self.assertIsNone(client.search_photos("cats", 1)[0].warning)

    def test_manifest_contains_source_and_license_metadata(self):
        photo = Photo(
            id="2",
            title="Cat",
            owner="Bee",
            page_url="https://page/2",
            download_url="https://image/2",
            license_id="4",
            license_name="CC BY 2.0",
            license_url="https://license/4",
            warning="Review terms",
        )
        with TemporaryDirectory() as directory:
            output = Path(directory) / "licenses.json"
            FlickrClient.write_license_manifest([photo], output)
            manifest = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(manifest[0]["license_name"], "CC BY 2.0")
        self.assertEqual(manifest[0]["page_url"], "https://page/2")
        self.assertEqual(manifest[0]["warning"], "Review terms")

    def test_license_api_failure_fails_closed(self):
        client = self.make_client()
        client.flickr.photos.licenses.getInfo.side_effect = RuntimeError("offline")

        self.assertEqual(client.search_photos("cats", 1), [])
        client.flickr.photos.search.assert_not_called()


if __name__ == "__main__":
    unittest.main()

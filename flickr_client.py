import asyncio
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from flickrapi import FlickrAPI


BLOCKED_LICENSE_IDS = frozenset({"0", "3", "6", "16"})
UNRESTRICTED_LICENSE_IDS = frozenset({"7", "8", "9", "10"})
SEARCHABLE_LICENSE_IDS = tuple(
    str(license_id)
    for license_id in range(17)
    if str(license_id) not in BLOCKED_LICENSE_IDS
)


@dataclass(frozen=True)
class Photo:
    id: str
    title: str
    owner: str
    page_url: str
    download_url: str
    license_id: str
    license_name: str
    license_url: str
    warning: Optional[str]


class FlickrClient:
    def __init__(self, api_key, api_secret):
        try:
            self.flickr = FlickrAPI(api_key, api_secret, format="parsed-json")
        except Exception as exc:
            print(f"Initialize Flickr client error: {exc}")
            raise

    def get_license_catalog(self):
        """Return Flickr's current license metadata keyed by numeric ID."""
        response = self.flickr.photos.licenses.getInfo()
        return {
            str(item["id"]): {
                "name": item.get("name", "Unknown license"),
                "url": item.get("url", ""),
            }
            for item in response["licenses"]["license"]
        }

    def search_photos(self, search_keyword, num_photos):
        """Find licensed photos, excluding restricted licenses at the API and locally."""
        if num_photos < 1:
            return []

        try:
            licenses = self.get_license_catalog()
            photos = self.flickr.photos.search(
                text=search_keyword,
                per_page=num_photos,
                license=",".join(SEARCHABLE_LICENSE_IDS),
                extras="url_o,license,owner_name",
            )
            results = []
            for item in photos["photos"]["photo"]:
                license_id = str(item.get("license", ""))
                # Defense in depth: never trust a remote filter alone.
                if not license_id or license_id in BLOCKED_LICENSE_IDS:
                    continue

                url = item.get("url_o") or self._largest_photo_url(item["id"])
                if not url:
                    continue

                license_info = licenses.get(
                    license_id, {"name": "Unknown license", "url": ""}
                )
                warning = None
                if license_id not in UNRESTRICTED_LICENSE_IDS:
                    warning = (
                        "Review this license's attribution, commercial-use, and "
                        "other conditions before publishing or reusing the image "
                        "or an AI-generated derivative."
                    )

                results.append(
                    Photo(
                        id=str(item["id"]),
                        title=item.get("title", ""),
                        owner=item.get("ownername") or item.get("owner", ""),
                        page_url=(
                            f"https://www.flickr.com/photos/"
                            f"{item['owner']}/{item['id']}"
                        ),
                        download_url=url,
                        license_id=license_id,
                        license_name=license_info["name"],
                        license_url=license_info["url"],
                        warning=warning,
                    )
                )
            return results
        except Exception as exc:
            print(f"Searching photo error: {exc}")
            return []

    def _largest_photo_url(self, photo_id):
        try:
            sizes = self.flickr.photos.getSizes(photo_id=photo_id)
            for size in reversed(sizes["sizes"]["size"]):
                if size.get("source"):
                    return size["source"]
        except Exception as exc:
            print(f"Acquire size of photo {photo_id} error: {exc}")
        return None

    @staticmethod
    def print_license_summary(photos):
        for index, photo in enumerate(photos, start=1):
            print(
                f"Photo {index}: {photo.license_name} (license {photo.license_id})\n"
                f"  Source: {photo.page_url}\n"
                f"  License: {photo.license_url or 'No license URL supplied by Flickr'}"
            )
            if photo.warning:
                print(f"  WARNING: {photo.warning}")

    @staticmethod
    def write_license_manifest(photos, filename="flickr_licenses.json"):
        Path(filename).write_text(
            json.dumps(
                [asdict(photo) for photo in photos], indent=2, ensure_ascii=False
            ),
            encoding="utf-8",
        )
        print(f"Saved license metadata to {filename}")

    async def download_photos(self, photos):
        import aiohttp

        self.print_license_summary(photos)
        self.write_license_manifest(photos)
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self._download_photo(
                        session, photo.download_url, f"photo_{index}.jpg"
                    )
                    for index, photo in enumerate(photos, start=1)
                ]
                await asyncio.gather(*tasks)
        except Exception as exc:
            print(f"Downloading photo error: {exc}")

    async def _download_photo(self, session, url, filename):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
                try:
                    with open(filename, "wb") as file:
                        file.write(content)
                    print(f"Downloaded {filename}")
                except Exception as exc:
                    print(f"Saving photo error: {exc}")
        except Exception as exc:
            print(f"Download {url} error: {exc}")

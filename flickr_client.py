from flickrapi import FlickrAPI
import asyncio

class FlickrClient:
    def __init__(self, api_key, api_secret):
        try:
            self.flickr = FlickrAPI(api_key, api_secret, format='parsed-json')
        except Exception as e:
            print(f"Initialize flickr client error:{e}")
            raise

    def search_photos(self, search_keyword, num_photos):
        try:
            photos = self.flickr.photos.search(
                text=search_keyword,
                per_page=num_photos,
                extras='url_o'
            )
            photo_urls = []
            for photo in photos['photos']['photo']:
                url = photo.get('url_o')
                if not url:
                    try:
                        sizes = self.flickr.photos.getSizes(photo_id=photo['id'])
                        for size in sizes['sizes']['size'][::-1]:
                            if 'source' in size:
                                url = size['source']
                                break
                    except Exception as e:
                        print(f"Acquire size of photo {photo['id']} error: {e}")
                        continue
                if url:
                    photo_urls.append(url)
            return photo_urls
        except Exception as e:
            print(f"Searching photo error: {e}")
            return []


    async def download_photos(self, urls):
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for idx, url in enumerate(urls):
                    filename = f'photo_{idx+1}.jpg'
                    tasks.append(self._download_photo(session, url, filename))
                await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Downloading photo error: {e}")

    async def _download_photo(self, session, url, filename):
        try:
            async with session.get(url) as response:
                content = await response.read()
                try:
                    with open(filename, 'wb') as f:
                        f.write(content)
                    print(f'Downloaded {filename}')
                except Exception as e:
                    print(f"Saving photo error: {e}")
        except Exception as e:
            print(f"Download {url} error: {e}")

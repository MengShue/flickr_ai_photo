from flickrapi import FlickrAPI
import asyncio

class FlickrClient:
    def __init__(self, api_key, api_secret):
        self.flickr = FlickrAPI(api_key, api_secret, format='parsed-json')

    def search_photos(self, search_keyword, num_photos):
        photos = self.flickr.photos.search(
            text=search_keyword,
            per_page=num_photos,
            extras='url_o'
        )
        photo_urls = []
        for photo in photos['photos']['photo']:
            url = photo.get('url_o')
            if not url:
                sizes = self.flickr.photos.getSizes(photo_id=photo['id'])
                for size in sizes['sizes']['size'][::-1]:
                    if 'source' in size:
                        url = size['source']
                        break
            if url:
                photo_urls.append(url)
        return photo_urls

    async def download_photos(self, urls):
        import aiohttp

        async with aiohttp.ClientSession() as session:
            tasks = []
            for idx, url in enumerate(urls):
                filename = f'photo_{idx+1}.jpg'
                tasks.append(self._download_photo(session, url, filename))
            await asyncio.gather(*tasks)

    async def _download_photo(self, session, url, filename):
        async with session.get(url) as response:
            content = await response.read()
            with open(filename, 'wb') as f:
                f.write(content)
            print(f'Downloaded {filename}')
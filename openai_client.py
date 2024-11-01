from openai import OpenAI
import aiohttp
import asyncio


class OpenAIClient:

    def __init__(self, api_key):
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Initialize OpenAI client error: {e}")
            raise

    async def generate_and_download_ai_images(self, photo_paths):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for idx, photo_path in enumerate(photo_paths):
                tasks.append(self._process_and_download(session, photo_path, idx))
            await asyncio.gather(*tasks)

    async def _process_and_download(self, session, photo_path, idx):
        from image_processor import ImageProcessor
        png_photo_path = ImageProcessor.process_image(photo_path)
        if not png_photo_path:
            print(f"Skip AI generated photo: Can't handle {photo_path}")
            return
        try:
            with open(png_photo_path, 'rb') as f:
                response = self.client.images.create_variation(
                    model="dall-e-2",
                    image=f,
                    n=1,
                    size="1024x1024"
                )

            ai_image_url = response.data[0].url
            print(f'URL of generated AI image：{ai_image_url}')
            ai_image_filename = f'ai_image_{idx+1}.png'
            await self._download_ai_image(session, ai_image_url, ai_image_filename)
        except Exception as e:
            print(f"Generating AI photo {photo_path} error: {e}")

    async def _download_ai_image(self, session, url, filename):
        try:
            async with session.get(url) as response:
                content = await response.read()
                with open(filename, 'wb') as f:
                    f.write(content)
                print(f'Downloaded AI image {filename}')
        except Exception as e:
            print(f"Download AI photo error: {e}")

import argparse
import asyncio
from flickr_client import FlickrClient
from openai_client import OpenAIClient
import os
from dotenv import load_dotenv

load_dotenv()

FLICKR_API_KEY = os.getenv('FLICKR_API_KEY')
FLICKR_API_SECRET = os.getenv('FLICKR_API_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Download Flickr images and generate AI images.')
    parser.add_argument('-s', '--search', required=True, help='Search keyword')
    parser.add_argument('-n', '--number', type=int, default=1, help='number of download images')
    parser.add_argument('-d', '--dalle', type=int, default=0, help='number of AI generated images')
    return parser.parse_args()

def main():
    args = parse_arguments()

    flickr_client = FlickrClient(FLICKR_API_KEY, FLICKR_API_SECRET)

    print('Searching...')
    photo_urls = flickr_client.search_photos(args.search, args.number)

    print('Downloading...')
    asyncio.run(flickr_client.download_photos(photo_urls))

    if args.dalle > 0:
        photo_paths = [f'photo_{i+1}.jpg' for i in range(args.dalle)]
        print('Generating AI images...')

        openai_client = OpenAIClient(OPENAI_API_KEY)
        asyncio.run(openai_client.generate_and_download_ai_images(photo_paths))

if __name__ == '__main__':
    main()

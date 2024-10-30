## Flickr Image Downloader and AI Image Generator

This Python program allows users to download images from Flickr based on a search keyword via the command line. Additionally, it can process the downloaded images using OpenAI’s DALL·E to generate AI variations of the images.

## Features

* Search and Download Images from Flickr: Specify a keyword to search for images and download them asynchronously.
* AI Image Generation => OpenAI DALL·E: Generate AI image variations using OpenAI’s DALL·E 2.
* Command Line Interface: Easily interact with the program using command-line arguments.

## Prerequisites

### Flickr API Key

You need to obtain a Flickr API key to use this program.

1. Visit the Flickr API Keys page: [Flickr API Keys](http://www.flickr.com/services/api/keys/ )
2. Apply for a new API key.
3. Set the Callback URL to http://localhost.
4. Note down your API Key and API Secret.

### OpenAI API Key (Optional)

If you wish to use the OpenAI DALL·E feature, you need an OpenAI API key.

1. Sign up or log in to your OpenAI account.
2. Navigate to the [API Keys](https://platform.openai.com/api-keys) page.
3. Generate a new secret key.
4. Note down your OpenAI API Key.

Note: If you choose not to use the AI feature, you do not need the OpenAI API key.

## Python Environment

* Python Version: Ensure you have Python 3.7 or higher installed.
* Virtual Environment: It’s recommended to use a virtual environment to manage dependencies.

## Installation

1. Clone the Repository

2.	Create and Activate Virtual Environment (Optional but Recommended)

```commandline
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install Dependencies

```commandline
pip install -r requirements.txt
```

## Configuration

1. Set API Keys
```commandline
# main.py
FLICKR_API_KEY = 'YOUR_FLICKR_API_KEY'
FLICKR_API_SECRET = 'YOUR_FLICKR_API_SECRET'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'  # Leave empty if not using OpenAI DALL·E
```

## Usage
Run the program using the command line:
```commandline
python main.py -s "search_keyword" -n NUMBER_OF_IMAGES -d NUMBER_OF_AI_IMAGES
```
### Arguments

	•	-s, --search: (Required) The search keyword to query images on Flickr.
	•	-n, --number: Number of images to download from Flickr. (Default: 1)
	•	-d, --dalle: Number of images to process using AI to generate variations. (Default: 0)

### Examples

#### Download 4 images of cats and generate 1 AI variation using DALL·E:
```commandline
python main.py -s "cat" -n 4 -d 1
```
#### Download 5 images of sunsets and generate 2 AI variations:
```commandline
python main.py -s "sunset" -n 5 -d 2
```

#### Download 3 images of mountains without AI processing:
```commandline
python main.py -s "mountain" -n 3
```

## Contact

For questions or suggestions, please contact meng.s.song@gmail.com.

Disclaimer: This project is for educational purposes. The author is not responsible for any misuse of the software.

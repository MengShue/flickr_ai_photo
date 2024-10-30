from PIL import Image


class ImageProcessor:

    # DALL E 2 input image must be a square PNG image less than 4MB in size.
    @staticmethod
    def process_image(filename):
        with Image.open(filename) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            min_dim = min(img.size)
            left = (img.width - min_dim) // 2
            top = (img.height - min_dim) // 2
            right = left + min_dim
            bottom = top + min_dim
            img = img.crop((left, top, right, bottom))
            img = img.resize((1024, 1024))
            png_filename = filename.rsplit('.', 1)[0] + '.png'
            img.save(png_filename, format='PNG')
            print(f'Processed and Saved {png_filename}')
            return png_filename

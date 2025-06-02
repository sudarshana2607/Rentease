from django.core.management.base import BaseCommand
import os
import requests
from PIL import Image
from io import BytesIO
from django.conf import settings

def download_image(url, filename, size=(800, 600)):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Create directory if it doesn't exist
            os.makedirs('rental_app/management/commands/sample_images', exist_ok=True)
            
            # Save the image
            img_path = os.path.join('rental_app/management/commands/sample_images', filename)
            img.save(img_path, 'JPEG', quality=85)
            print(f'Downloaded: {img_path}')
            return True
    except Exception as e:
        print(f'Error downloading {filename}: {str(e)}')
    return False

def download_property_images():
    """
    Downloads sample property images for different BHK configurations.
    """
    # Create the sample_images directory if it doesn't exist
    sample_images_dir = os.path.join('rental_app/management/commands/sample_images')
    os.makedirs(sample_images_dir, exist_ok=True)

    # Sample image URLs for different BHK configurations
    image_urls = {
        '1bhk_1_1.jpg': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267',
        '1bhk_1_2.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        '1bhk_1_3.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        
        '1bhk_2_1.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
        '1bhk_2_2.jpg': 'https://images.unsplash.com/photo-1505693314120-0d443867891c',
        '1bhk_2_3.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
        
        '1bhk_3_1.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        '1bhk_3_2.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        '1bhk_3_3.jpg': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267',
        
        '2bhk_1_1.jpg': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750',
        '2bhk_1_2.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        '2bhk_1_3.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        
        '2bhk_2_1.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
        '2bhk_2_2.jpg': 'https://images.unsplash.com/photo-1505693314120-0d443867891c',
        '2bhk_2_3.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        
        '2bhk_3_1.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        '2bhk_3_2.jpg': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267',
        '2bhk_3_3.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
        
        '3bhk_1_1.jpg': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750',
        '3bhk_1_2.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        '3bhk_1_3.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        
        '3bhk_2_1.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
        '3bhk_2_2.jpg': 'https://images.unsplash.com/photo-1505693314120-0d443867891c',
        '3bhk_2_3.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        
        '3bhk_3_1.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        '3bhk_3_2.jpg': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267',
        '3bhk_3_3.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
        
        '4bhk_1_1.jpg': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750',
        '4bhk_1_2.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        '4bhk_1_3.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        
        '4bhk_2_1.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
        '4bhk_2_2.jpg': 'https://images.unsplash.com/photo-1505693314120-0d443867891c',
        '4bhk_2_3.jpg': 'https://images.unsplash.com/photo-1505843513577-22bb7d21e455',
        
        '4bhk_3_1.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
        '4bhk_3_2.jpg': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267',
        '4bhk_3_3.jpg': 'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6',
    }

    # Download each image
    for filename, url in image_urls.items():
        filepath = os.path.join(sample_images_dir, filename)
        if not os.path.exists(filepath):
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f'Downloaded {filename}')
            except Exception as e:
                print(f'Error downloading {filename}: {str(e)}')

class Command(BaseCommand):
    help = 'Downloads sample property images from Unsplash'

    def handle(self, *args, **kwargs):
        download_property_images()
        self.stdout.write(self.style.SUCCESS('Successfully downloaded all property images')) 
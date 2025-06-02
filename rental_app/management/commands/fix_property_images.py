from django.core.management.base import BaseCommand
from rental_app.models import Property
import os
from django.conf import settings
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Fixes property images by ensuring each property has a proper image'

    def handle(self, *args, **kwargs):
        # Create media directory if it doesn't exist
        media_dir = os.path.join(settings.MEDIA_ROOT, 'property_images')
        os.makedirs(media_dir, exist_ok=True)

        # Get all properties
        properties = Property.objects.all()
        
        # Sample image paths for different BHK types
        sample_images = {
            '1BHK': [
                '1bhk_1_1.jpg',
                '1bhk_2_1.jpg',
                '1bhk_3_1.jpg'
            ],
            '2BHK': [
                '2bhk_1_1.jpg',
                '2bhk_2_1.jpg',
                '2bhk_3_1.jpg'
            ],
            '3BHK': [
                '3bhk_1_1.jpg',
                '3bhk_2_1.jpg',
                '3bhk_3_1.jpg'
            ],
            '4BHK': [
                '4bhk_1_1.jpg',
                '4bhk_2_1.jpg',
                '4bhk_3_1.jpg'
            ]
        }

        # Fix each property's image
        for property in properties:
            try:
                # Get the appropriate sample image based on BHK type
                bhk_type = property.bhk
                if bhk_type in sample_images:
                    # Use the first image from the list for this BHK type
                    sample_image = sample_images[bhk_type][0]
                    
                    # Source path in the sample_images directory
                    source_path = os.path.join(
                        settings.BASE_DIR,
                        'rental_app',
                        'management',
                        'commands',
                        'sample_images',
                        sample_image
                    )
                    
                    # Destination path in the media directory
                    dest_path = os.path.join(media_dir, sample_image)
                    
                    # Copy the image if it exists
                    if os.path.exists(source_path):
                        shutil.copy2(source_path, dest_path)
                        # Create or update PropertyImage
                        from rental_app.models import PropertyImage
                        PropertyImage.objects.update_or_create(
                            property=property,
                            is_primary=True,
                            defaults={'image': f'property_images/{sample_image}'}
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully fixed image for property {property.title}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Sample image not found: {source_path}'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'No sample images available for BHK type: {bhk_type}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error fixing image for property {property.title}: {str(e)}'
                    )
                )

        self.stdout.write(self.style.SUCCESS('Finished fixing property images')) 
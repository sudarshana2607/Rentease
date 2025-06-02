from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rental_app.models import UserProfile, Property, PropertyImage
from django.core.files import File
import os
from .download_property_images import download_property_images

class Command(BaseCommand):
    help = 'Adds sample properties with images to the database'

    def handle(self, *args, **kwargs):
        # Download real property images first
        download_property_images()
        
        # Create a sample landlord if not exists
        landlord_user, created = User.objects.get_or_create(
            username='landlord1',
            defaults={
                'email': 'landlord1@example.com',
                'is_staff': True
            }
        )
        if created:
            landlord_user.set_password('landlord123')
            landlord_user.save()
            landlord_profile = UserProfile.objects.create(
                user=landlord_user,
                user_type='landlord',
                phone_number='1234567890',
                address='123 Main Street, City'
            )
            self.stdout.write(self.style.SUCCESS('Created sample landlord account'))
        else:
            landlord_profile = landlord_user.userprofile

        # Sample properties data with better price distribution
        properties_data = [
            # 1BHK Properties
            {
                'title': 'Budget 1BHK Studio',
                'description': 'Compact and affordable 1BHK studio apartment perfect for singles or couples. Built in 2010.',
                'address': '123 Main Street, City',
                'price': 15000,
                'bhk': '1BHK',
                'model_type': 'house',
                'year_built': 2010,
                'images': ['1bhk_1_1.jpg', '1bhk_1_2.jpg', '1bhk_1_3.jpg']
            },
            {
                'title': 'Modern 1BHK Apartment',
                'description': 'Contemporary 1BHK apartment with modern amenities and great location. Built in 2020.',
                'address': '456 Park Avenue, City',
                'price': 25000,
                'bhk': '1BHK',
                'model_type': 'apartment',
                'year_built': 2020,
                'images': ['1bhk_2_1.jpg', '1bhk_2_2.jpg', '1bhk_2_3.jpg']
            },
            {
                'title': 'Premium 1BHK Flat',
                'description': 'Luxurious 1BHK flat with premium finishes and amenities. Built in 2022.',
                'address': '789 Luxury Lane, City',
                'price': 45000,
                'bhk': '1BHK',
                'model_type': 'apartment',
                'year_built': 2022,
                'images': ['1bhk_3_1.jpg', '1bhk_3_2.jpg', '1bhk_3_3.jpg']
            },
            {
                'title': 'Executive 1BHK Suite',
                'description': 'Executive 1BHK suite with premium amenities and city views. Built in 2023.',
                'address': '101 Business District, City',
                'price': 65000,
                'bhk': '1BHK',
                'model_type': 'apartment',
                'year_built': 2023,
                'images': ['1bhk_1_1.jpg', '1bhk_1_2.jpg', '1bhk_1_3.jpg']
            },
            {
                'title': 'Luxury 1BHK Penthouse',
                'description': 'Exclusive 1BHK penthouse with panoramic views and luxury amenities. Built in 2023.',
                'address': '202 Sky Tower, City',
                'price': 85000,
                'bhk': '1BHK',
                'model_type': 'apartment',
                'year_built': 2023,
                'images': ['1bhk_2_1.jpg', '1bhk_2_2.jpg', '1bhk_2_3.jpg']
            },
            {
                'title': 'Premium 1BHK Villa',
                'description': 'Premium 1BHK villa with private garden and luxury finishes. Built in 2023.',
                'address': '303 Elite Gardens, City',
                'price': 120000,
                'bhk': '1BHK',
                'model_type': 'villa',
                'year_built': 2023,
                'images': ['1bhk_3_1.jpg', '1bhk_3_2.jpg', '1bhk_3_3.jpg']
            },
            {
                'title': 'Ultra Luxury 1BHK Suite',
                'description': 'Ultra luxury 1BHK suite with premium amenities and exclusive services. Built in 2024.',
                'address': '404 Platinum Heights, City',
                'price': 150000,
                'bhk': '1BHK',
                'model_type': 'apartment',
                'year_built': 2024,
                'images': ['1bhk_1_1.jpg', '1bhk_1_2.jpg', '1bhk_1_3.jpg']
            },
            {
                'title': 'Royal 1BHK Penthouse',
                'description': 'Royal 1BHK penthouse with panoramic views and exclusive amenities. Built in 2024.',
                'address': '505 Royal Towers, City',
                'price': 200000,
                'bhk': '1BHK',
                'model_type': 'apartment',
                'year_built': 2024,
                'images': ['1bhk_2_1.jpg', '1bhk_2_2.jpg', '1bhk_2_3.jpg']
            },
            
            # 2BHK Properties
            {
                'title': 'Affordable 2BHK Apartment',
                'description': 'Spacious 2BHK apartment at an affordable price. Built in 2015.',
                'address': '606 Budget Street, City',
                'price': 35000,
                'bhk': '2BHK',
                'model_type': 'house',
                'year_built': 2015,
                'images': ['2bhk_1_1.jpg', '2bhk_1_2.jpg', '2bhk_1_3.jpg']
            },
            {
                'title': 'Family 2BHK Flat',
                'description': 'Comfortable 2BHK flat perfect for small families. Built in 2020.',
                'address': '707 Family Avenue, City',
                'price': 55000,
                'bhk': '2BHK',
                'model_type': 'apartment',
                'year_built': 2020,
                'images': ['2bhk_2_1.jpg', '2bhk_2_2.jpg', '2bhk_2_3.jpg']
            },
            {
                'title': 'Luxury 2BHK Apartment',
                'description': 'Luxurious 2BHK apartment with premium amenities. Built in 2022.',
                'address': '808 Luxury Lane, City',
                'price': 75000,
                'bhk': '2BHK',
                'model_type': 'apartment',
                'year_built': 2022,
                'images': ['2bhk_3_1.jpg', '2bhk_3_2.jpg', '2bhk_3_3.jpg']
            },
            {
                'title': 'Executive 2BHK Suite',
                'description': 'Executive 2BHK suite with premium finishes and amenities. Built in 2023.',
                'address': '909 Business District, City',
                'price': 95000,
                'bhk': '2BHK',
                'model_type': 'apartment',
                'year_built': 2023,
                'images': ['2bhk_1_1.jpg', '2bhk_1_2.jpg', '2bhk_1_3.jpg']
            },
            {
                'title': 'Premium 2BHK Villa',
                'description': 'Premium 2BHK villa with private garden and luxury amenities. Built in 2023.',
                'address': '1010 Elite Gardens, City',
                'price': 150000,
                'bhk': '2BHK',
                'model_type': 'villa',
                'year_built': 2023,
                'images': ['2bhk_2_1.jpg', '2bhk_2_2.jpg', '2bhk_2_3.jpg']
            },
            {
                'title': 'Royal 2BHK Penthouse',
                'description': 'Royal 2BHK penthouse with panoramic views and exclusive amenities. Built in 2024.',
                'address': '1111 Royal Towers, City',
                'price': 200000,
                'bhk': '2BHK',
                'model_type': 'apartment',
                'year_built': 2024,
                'images': ['2bhk_3_1.jpg', '2bhk_3_2.jpg', '2bhk_3_3.jpg']
            },
            
            # 3BHK Properties
            {
                'title': 'Budget 3BHK Villa',
                'description': 'Spacious 3BHK villa at an affordable price. Built in 2015.',
                'address': '1212 Budget Street, City',
                'price': 45000,
                'bhk': '3BHK',
                'model_type': 'villa',
                'year_built': 2015,
                'images': ['3bhk_1_1.jpg', '3bhk_1_2.jpg', '3bhk_1_3.jpg']
            },
            {
                'title': 'Modern 3BHK Apartment',
                'description': 'Contemporary 3BHK apartment with modern amenities. Built in 2020.',
                'address': '1313 Modern Avenue, City',
                'price': 75000,
                'bhk': '3BHK',
                'model_type': 'apartment',
                'year_built': 2020,
                'images': ['3bhk_2_1.jpg', '3bhk_2_2.jpg', '3bhk_2_3.jpg']
            },
            {
                'title': 'Premium 3BHK Villa',
                'description': 'Premium 3BHK villa with luxury amenities and garden. Built in 2022.',
                'address': '1414 Premium Lane, City',
                'price': 120000,
                'bhk': '3BHK',
                'model_type': 'villa',
                'year_built': 2022,
                'images': ['3bhk_3_1.jpg', '3bhk_3_2.jpg', '3bhk_3_3.jpg']
            },
            {
                'title': 'Luxury 3BHK Penthouse',
                'description': 'Luxurious 3BHK penthouse with panoramic views. Built in 2023.',
                'address': '1515 Luxury Heights, City',
                'price': 180000,
                'bhk': '3BHK',
                'model_type': 'apartment',
                'year_built': 2023,
                'images': ['3bhk_1_1.jpg', '3bhk_1_2.jpg', '3bhk_1_3.jpg']
            },
            {
                'title': 'Royal 3BHK Villa',
                'description': 'Royal 3BHK villa with exclusive amenities and services. Built in 2024.',
                'address': '1616 Royal Gardens, City',
                'price': 200000,
                'bhk': '3BHK',
                'model_type': 'villa',
                'year_built': 2024,
                'images': ['3bhk_2_1.jpg', '3bhk_2_2.jpg', '3bhk_2_3.jpg']
            },
            
            # 4BHK Properties
            {
                'title': 'Budget 4BHK Villa',
                'description': 'Spacious 4BHK villa at an affordable price. Built in 2015.',
                'address': '1717 Budget Street, City',
                'price': 48000,
                'bhk': '4BHK',
                'model_type': 'villa',
                'year_built': 2015,
                'images': ['4bhk_1_1.jpg', '4bhk_1_2.jpg', '4bhk_1_3.jpg']
            },
            {
                'title': 'Affordable 4BHK Apartment',
                'description': 'Comfortable 4BHK apartment perfect for large families. Built in 2020.',
                'address': '1718 Family Avenue, City',
                'price': 65000,
                'bhk': '4BHK',
                'model_type': 'apartment',
                'year_built': 2020,
                'images': ['4bhk_2_1.jpg', '4bhk_2_2.jpg', '4bhk_2_3.jpg']
            },
            {
                'title': 'Modern 4BHK Apartment',
                'description': 'Contemporary 4BHK apartment with modern amenities. Built in 2020.',
                'address': '1818 Modern Avenue, City',
                'price': 95000,
                'bhk': '4BHK',
                'model_type': 'apartment',
                'year_built': 2020,
                'images': ['4bhk_2_1.jpg', '4bhk_2_2.jpg', '4bhk_2_3.jpg']
            },
            {
                'title': 'Premium 4BHK Villa',
                'description': 'Premium 4BHK villa with luxury amenities and garden. Built in 2022.',
                'address': '1919 Premium Lane, City',
                'price': 180000,
                'bhk': '4BHK',
                'model_type': 'villa',
                'year_built': 2022,
                'images': ['4bhk_3_1.jpg', '4bhk_3_2.jpg', '4bhk_3_3.jpg']
            },
            {
                'title': 'Luxury 4BHK Penthouse',
                'description': 'Luxurious 4BHK penthouse with panoramic views. Built in 2023.',
                'address': '2020 Luxury Heights, City',
                'price': 250000,
                'bhk': '4BHK',
                'model_type': 'apartment',
                'year_built': 2023,
                'images': ['4bhk_1_1.jpg', '4bhk_1_2.jpg', '4bhk_1_3.jpg']
            }
        ]

        # Add properties
        for prop_data in properties_data:
            property_obj = Property.objects.create(
                landlord=landlord_profile,
                title=prop_data['title'],
                description=prop_data['description'],
                address=prop_data['address'],
                price=prop_data['price'],
                bhk=prop_data['bhk'],
                model_type=prop_data['model_type'],
                year_built=prop_data['year_built']
            )

            # Add images for the property
            for image_name in prop_data['images']:
                image_path = os.path.join('rental_app/management/commands/sample_images', image_name)
                if not os.path.exists(image_path):
                    self.stdout.write(self.style.WARNING(f'Image not found: {image_path} (skipping)'))
                    continue
                with open(image_path, 'rb') as f:
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=File(f, name=image_name),
                        is_primary=(image_name == prop_data['images'][0])
                    )

            self.stdout.write(self.style.SUCCESS(f'Added property: {prop_data["title"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully added all sample properties')) 
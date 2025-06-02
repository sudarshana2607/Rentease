import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_system.settings')
django.setup()

from rental_app.models import Property

# Update construction years for all properties
properties = Property.objects.all()

# Assign years based on property type and model
for property in properties:
    if property.model_type == 'new':
        # Newer properties (2018-2024)
        if property.bhk == '1BHK':
            property.year_built = 2020
        elif property.bhk == '2BHK':
            property.year_built = 2021
        elif property.bhk == '3BHK':
            property.year_built = 2022
        else:  # 4BHK
            property.year_built = 2023
    else:
        # Older properties (2010-2017)
        if property.bhk == '1BHK':
            property.year_built = 2015
        elif property.bhk == '2BHK':
            property.year_built = 2016
        elif property.bhk == '3BHK':
            property.year_built = 2017
        else:  # 4BHK
            property.year_built = 2018
    
    property.save()
    print(f"Updated {property.title} - Year Built: {property.year_built}")

print("All properties have been updated with construction years!") 
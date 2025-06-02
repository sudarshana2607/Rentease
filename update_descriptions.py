import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_system.settings')
django.setup()

from rental_app.models import Property

# Update descriptions for all properties
properties = Property.objects.all()

for property in properties:
    # Get the year built
    year_built = property.year_built
    
    # Update the description to include the year
    if year_built:
        # Check if the description already mentions the year
        if str(year_built) not in property.description:
            # Add the year to the beginning of the description
            property.description = f"Built in {year_built}. {property.description}"
            property.save()
            print(f"Updated description for {property.title}")

print("All property descriptions have been updated with construction years!") 
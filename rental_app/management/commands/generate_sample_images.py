from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_image(filename, title, color):
    # Create a new image with a white background
    img = Image.new('RGB', (800, 600), color)
    draw = ImageDraw.Draw(img)
    
    # Add some text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Add title
    draw.text((400, 300), title, fill='white', font=font, anchor="mm")
    
    # Save the image
    img.save(filename)

def generate_images():
    # Create sample_images directory if it doesn't exist
    os.makedirs('rental_app/management/commands/sample_images', exist_ok=True)
    
    # Generate images for each property
    properties = [
        # Modern 2BHK Apartment
        ('property1.jpg', 'Modern 2BHK', '#2E86C1'),
        ('property1_2.jpg', 'Living Room', '#3498DB'),
        ('property1_3.jpg', 'Kitchen View', '#2980B9'),
        
        # Luxury 3BHK Villa
        ('property2.jpg', 'Luxury 3BHK', '#27AE60'),
        ('property2_2.jpg', 'Garden View', '#2ECC71'),
        ('property2_3.jpg', 'Master Bedroom', '#1E8449'),
        
        # Cozy 1BHK Studio
        ('property3.jpg', 'Cozy 1BHK', '#E74C3C'),
        ('property3_2.jpg', 'Modern Kitchen', '#EC7063'),
        ('property3_3.jpg', 'Living Area', '#C0392B'),
        
        # Premium 4BHK Penthouse
        ('property4.jpg', 'Premium 4BHK', '#8E44AD'),
        ('property4_2.jpg', 'Penthouse View', '#9B59B6'),
        ('property4_3.jpg', 'Terrace', '#6C3483'),
        
        # Affordable 2BHK Flat
        ('property5.jpg', 'Affordable 2BHK', '#F39C12'),
        ('property5_2.jpg', 'Balcony View', '#F1C40F'),
        ('property5_3.jpg', 'Bedroom', '#D35400'),
        
        # New Properties
        # Luxury 2BHK Apartment
        ('property6.jpg', 'Luxury 2BHK', '#16A085'),
        ('property6_2.jpg', 'Modern Interior', '#1ABC9C'),
        ('property6_3.jpg', 'Bathroom', '#0E6655'),
        
        # Spacious 3BHK Flat
        ('property7.jpg', 'Spacious 3BHK', '#D35400'),
        ('property7_2.jpg', 'Living Space', '#E67E22'),
        ('property7_3.jpg', 'Dining Area', '#A04000'),
        
        # Premium 1BHK Studio
        ('property8.jpg', 'Premium 1BHK', '#2C3E50'),
        ('property8_2.jpg', 'Studio View', '#34495E'),
        ('property8_3.jpg', 'Modern Design', '#1A252F'),
        
        # Family 4BHK Villa
        ('property9.jpg', 'Family 4BHK', '#7D3C98'),
        ('property9_2.jpg', 'Garden', '#9B59B6'),
        ('property9_3.jpg', 'Living Room', '#6C3483'),
        
        # Budget 1BHK Flat
        ('property10.jpg', 'Budget 1BHK', '#1A5276'),
        ('property10_2.jpg', 'Compact Kitchen', '#2874A6'),
        ('property10_3.jpg', 'Living Area', '#154360')
    ]
    
    for filename, title, color in properties:
        filepath = os.path.join('rental_app/management/commands/sample_images', filename)
        create_sample_image(filepath, title, color)
        print(f'Created image: {filename}')

if __name__ == '__main__':
    generate_images() 
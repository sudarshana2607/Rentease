from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import Property, PropertyImage, Review, Complaint, Booking, UserProfile, Payment, Notification
from .forms import ReviewForm, ComplaintForm, PropertyImageForm, BookingForm, UserRegistrationForm, PropertyForm
import logging
from django.utils import timezone
from django.contrib.auth import logout
import random 
# Rest of your imports...




logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def dashboard(request):
    try:
        user_profile = request.user.userprofile
    except Exception:
        messages.error(request, 'Your account is missing a profile. Please log in again.')
        logout(request)
        return redirect('login')
    context = {}
    
    if user_profile.user_type == 'landlord':
        properties = Property.objects.filter(landlord=user_profile)
        bookings = Booking.objects.filter(property__landlord=user_profile)
    else:  # tenant
        properties = Property.objects.filter(is_available=True)
        bookings = Booking.objects.filter(tenant=user_profile)
    
    context.update({
        'user_profile': user_profile,
        'properties': properties,
        'bookings': bookings,
    })
    
    return render(request, 'rental_app/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                user_type=form.cleaned_data['user_type'],
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address']
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'rental_app/register.html', {'form': form})

@login_required
def property_list(request):
    properties = Property.objects.filter(is_available=True)
    
    # Get filter parameters
    bhk = request.GET.get('bhk')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    model_type = request.GET.get('model_type')
    
    # Apply filters
    if bhk:
        properties = properties.filter(bhk=bhk)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if model_type:
        properties = properties.filter(model_type=model_type)
    
    # Get unique values for filter options
    bhk_choices = Property.BHK_CHOICES
    model_type_choices = Property.MODEL_TYPE_CHOICES
    
    context = {
        'properties': properties,
        'bhk_choices': bhk_choices,
        'model_type_choices': model_type_choices,
        'current_filters': {
            'bhk': bhk,
            'min_price': min_price,
            'max_price': max_price,
            'model_type': model_type,
        }
    }
    return render(request, 'rental_app/property_list.html', context)

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user.userprofile
            property.save()
            
            # Handle images
            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    PropertyImage.objects.create(property=property, image=image)
            else:
                # Use default image if no images uploaded
                PropertyImage.objects.create(
                    property=property,
                    image='property_images/default_property.jpg',
                    is_primary=True
                )
            
            messages.success(request, 'Property added successfully!')
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'rental_app/add_property.html', {'form': form})

@login_required
def book_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    logger.info(f"Attempting to book property {pk} by user {request.user.username}")
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create the booking
                    booking = form.save(commit=False)
                    booking.property = property
                    booking.tenant = request.user.userprofile
                    booking.status = 'pending'
                    booking.save()
                    logger.info(f"Created booking {booking.id} for property {property.title}")
                    
                    # Create a payment record
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=property.price,
                        status='pending'
                    )
                    logger.info(f"Created payment record {payment.id} for booking {booking.id}")
                    
                    # Add debug message
                    messages.info(request, f'Booking created with ID: {booking.id}')
                
                messages.success(request, 'Booking request submitted successfully! Please wait for landlord approval.')
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error creating booking: {str(e)}")
                messages.error(request, f'Error creating booking: {str(e)}')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = BookingForm()
    return render(request, 'rental_app/book_property.html', {'form': form, 'property': property})

@login_required
def submit_complaint(request, property_pk):
    property = get_object_or_404(Property, pk=property_pk)
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.property = property
            complaint.tenant = request.user.userprofile
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
            return redirect('property_detail', pk=property_pk)
    else:
        form = ComplaintForm()
    return render(request, 'rental_app/property_detail.html', {'form': form, 'property': property})

@login_required
def manage_bookings(request):
    user_profile = request.user.userprofile
    logger.info(f"Managing bookings for user {request.user.username} (type: {user_profile.user_type})")
    
    try:
        if user_profile.user_type == 'landlord':
            # Get all bookings for properties owned by this landlord
            bookings = Booking.objects.filter(
                property__landlord=user_profile
            ).select_related(
                'property',
                'tenant',
                'tenant__user'
            ).order_by('-created_at')
            
            # Debug information
            logger.info(f"Found {bookings.count()} bookings for landlord {request.user.username}")
            messages.info(request, f'Found {bookings.count()} bookings for your properties')
            
            # Log each booking for debugging
            for booking in bookings:
                logger.info(
                    f"Booking ID: {booking.id}, "
                    f"Property: {booking.property.title}, "
                    f"Tenant: {booking.tenant.user.username}, "
                    f"Status: {booking.status}, "
                    f"Created: {booking.created_at}"
                )
                messages.info(request, f'Booking {booking.id}: {booking.property.title} by {booking.tenant.user.username}')
                
        else:  # tenant view
            bookings = Booking.objects.filter(
                tenant=user_profile
            ).select_related(
                'property',
                'property__landlord',
                'property__landlord__user'
            ).order_by('-created_at')
            
            logger.info(f"Found {bookings.count()} bookings for tenant {request.user.username}")
            messages.info(request, f'Found {bookings.count()} bookings for you')
            
    except Exception as e:
        logger.error(f"Error in manage_bookings: {str(e)}")
        messages.error(request, f'Error loading bookings: {str(e)}')
        bookings = []
    
    context = {
        'bookings': bookings,
        'has_bookings': bookings.exists(),
        'user_type': user_profile.user_type
    }
    return render(request, 'rental_app/manage_bookings.html', context)

@login_required
def update_booking_status(request, booking_id, status):
    logger.info(f"Updating booking {booking_id} status to {status} by user {request.user.username}")
    
    try:
        booking = get_object_or_404(Booking, pk=booking_id)
        if request.user.userprofile == booking.property.landlord:
            with transaction.atomic():
                booking.status = status
                booking.save()
                logger.info(f"Updated booking {booking_id} status to {status}")
                
                # Update payment status if booking is accepted
                if status == 'accepted':
                    payment = Payment.objects.get(booking=booking)
                    payment.status = 'pending'
                    payment.save()
                    logger.info(f"Updated payment status for booking {booking_id}")
            
            messages.success(request, f'Booking {status} successfully!')
        else:
            logger.warning(f"Unauthorized status update attempt by {request.user.username}")
            messages.error(request, 'You are not authorized to update this booking.')
    except Exception as e:
        logger.error(f"Error updating booking status: {str(e)}")
        messages.error(request, f'Error updating booking: {str(e)}')
    
    return redirect('manage_bookings')

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.user.userprofile == booking.property.landlord:
        booking.delete()
        messages.success(request, 'Booking deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this booking.')
    return redirect('manage_bookings')

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    images = property.images.all()
    reviews = property.reviews.all().order_by('-created_at')
    complaints = property.complaints.all().order_by('-created_at')
    
    # Initialize forms
    review_form = None
    complaint_form = None
    image_form = None
    booking_form = None
    
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            if user_profile.user_type == 'tenant':
                review_form = ReviewForm()
                complaint_form = ComplaintForm()
                booking_form = BookingForm()
            elif user_profile.user_type == 'landlord' and user_profile == property.landlord:
                image_form = PropertyImageForm()
                # Allow landlords to see and respond to complaints
                complaint_form = ComplaintForm()
        except:
            pass  # Handle case where user has no profile
    
    context = {
        'property': property,
        'images': images,
        'reviews': reviews,
        'complaints': complaints,
        'review_form': review_form,
        'complaint_form': complaint_form,
        'image_form': image_form,
        'booking_form': booking_form,
        'is_landlord': request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'landlord' and request.user.userprofile == property.landlord
    }
    
    return render(request, 'rental_app/property_detail.html', context)

def create_test_data(request):
    """Create test data for the rental system"""
    try:
        # Create landlords
        landlords = [
            {
                'username': 'landlord1',
                'email': 'landlord1@test.com',
                'password': 'testpass123',
                'name': 'John Smith',
                'phone': '1234567890',
                'address': '123 Main St'
            },
            {
                'username': 'landlord2',
                'email': 'landlord2@test.com',
                'password': 'testpass123',
                'name': 'Sarah Johnson',
                'phone': '2345678901',
                'address': '456 Oak Ave'
            },
            {
                'username': 'landlord3',
                'email': 'landlord3@test.com',
                'password': 'testpass123',
                'name': 'Michael Brown',
                'phone': '3456789012',
                'address': '789 Pine Rd'
            }
        ]

        # Create tenants
        tenants = [
            {
                'username': 'tenant1',
                'email': 'tenant1@test.com',
                'password': 'testpass123',
                'name': 'Alice Wilson',
                'phone': '4567890123',
                'address': '321 Elm St'
            },
            {
                'username': 'tenant2',
                'email': 'tenant2@test.com',
                'password': 'testpass123',
                'name': 'Bob Davis',
                'phone': '5678901234',
                'address': '654 Maple Dr'
            },
            {
                'username': 'tenant3',
                'email': 'tenant3@test.com',
                'password': 'testpass123',
                'name': 'Carol White',
                'phone': '6789012345',
                'address': '987 Cedar Ln'
            }
        ]

        # Create users and profiles
        for user_data in landlords + tenants:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['name'].split()[0],
                    last_name=user_data['name'].split()[1]
                )
                UserProfile.objects.create(
                    user=user,
                    user_type='landlord' if user_data in landlords else 'tenant',
                    phone_number=user_data['phone'],
                    address=user_data['address']
                )

        # Create properties for each landlord
        for landlord_data in landlords:
            landlord = User.objects.get(username=landlord_data['username']).userprofile
            for i in range(2):  # 2 properties per landlord
                property = Property.objects.create(
                    title=f"{landlord_data['name']}'s Property {i+1}",
                    description=f"Beautiful property {i+1} by {landlord_data['name']}",
                    address=f"{landlord_data['address']} Unit {i+1}",
                    bhk=2,
                    price=1000 + (i * 500),
                    model_type='apartment',
                    year_built=2020,
                    landlord=landlord,
                    is_available=True
                )
                # Add default image
                PropertyImage.objects.create(
                    property=property,
                    image='property_images/default_property.jpg',
                    is_primary=True
                )

        messages.success(request, 'Test data created successfully!')
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error creating test data: {str(e)}')
        return redirect('dashboard')

def create_landlords(request):
    """Create the specified landlords in the system"""
    try:
        # Create landlords
        landlords = [
            {
                'username': 'jaanu',
                'email': 'jaanu@gmail.com',
                'password': 'jaanu123',  # Default password
                'name': 'janani',
                'phone': '1234567890',
                'address': 'jazz1234'
            },
            {
                'username': 'thejas',
                'email': 'thejas@gmail.com',
                'password': 'thejas123',  # Default password
                'name': 'thejas ravichandran',
                'phone': '2244557799',
                'address': 'teja0011'
            },
            {
                'username': 'sunny',
                'email': 'sunny@gmail.com',
                'password': 'sunny123',  # Default password
                'name': 'sania malhothra',
                'phone': '0987654321',
                'address': 'sanimahi'
            }
        ]

        # Create users and profiles
        for user_data in landlords:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['name'].split()[0],
                    last_name=' '.join(user_data['name'].split()[1:]) if len(user_data['name'].split()) > 1 else ''
                )
                UserProfile.objects.create(
                    user=user,
                    user_type='landlord',
                    phone_number=user_data['phone'],
                    address=user_data['address']
                )
                messages.success(request, f'Created landlord account for {user_data["username"]}')
            else:
                messages.info(request, f'Landlord {user_data["username"]} already exists')

        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error creating landlords: {str(e)}')
        return redirect('dashboard')

def create_tenants(request):
    """Create the specified tenants in the system"""
    try:
        # Create tenants
        tenants = [
            {
                'username': 'aaadi',
                'email': 'aadi@gmail.com',
                'password': 'aadi123',  # Default password
                'name': 'aaditya arun',
                'phone': '23456789',
                'address': 'aadi1122'
            },
            {
                'username': 'ajju',
                'email': 'arjun@gmail.com',
                'password': 'ajju123',  # Default password
                'name': 'arjun sharma',
                'phone': '9999900000',
                'address': 'ajju5566'
            },
            {
                'username': 'aarna',
                'email': 'aarna@gmail.com',
                'password': 'aarna123',  # Default password
                'name': 'aarna avyuth',
                'phone': '1111100000',
                'address': 'aarna@26'
            }
        ]

        # Create users and profiles
        for user_data in tenants:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['name'].split()[0],
                    last_name=' '.join(user_data['name'].split()[1:]) if len(user_data['name'].split()) > 1 else ''
                )
                UserProfile.objects.create(
                    user=user,
                    user_type='tenant',
                    phone_number=user_data['phone'],
                    address=user_data['address']
                )
                messages.success(request, f'Created tenant account for {user_data["username"]}')
            else:
                messages.info(request, f'Tenant {user_data["username"]} already exists')

        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error creating tenants: {str(e)}')
        return redirect('dashboard')

def create_new_landlords(request):
    """Create new landlords and their properties"""
    try:
        # Delete existing properties and landlords
        Property.objects.all().delete()
        UserProfile.objects.filter(user_type='landlord').delete()
        User.objects.filter(userprofile__user_type='landlord').delete()

        # Create new landlords
        landlords = [
            {
                'username': 'akshu',
                'email': 'akshay@gmail.com',
                'password': 'akshu123',  # Default password
                'name': 'akshay vikas',
                'phone': '7777755555',
                'address': 'akshu234'
            },
            {
                'username': 'luxx',
                'email': 'laksh@gmail.com',
                'password': 'luxx123',  # Default password
                'name': 'lakshana sri',
                'phone': '2222244444',
                'address': 'lux@2702'
            },
            {
                'username': 'nethu',
                'email': 'nethra@gmail.com',
                'password': 'nethu123',  # Default password
                'name': 'nethra sivakumar',
                'phone': '1111133333',
                'address': 'nethu@71'
            }
        ]

        # Create users, profiles, and properties
        for user_data in landlords:
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['name'].split()[0],
                last_name=' '.join(user_data['name'].split()[1:]) if len(user_data['name'].split()) > 1 else ''
            )
            
            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                user_type='landlord',
                phone_number=user_data['phone'],
                address=user_data['address']
            )
            
            # Create properties for each landlord
            for i in range(2):  # 2 properties per landlord
                property = Property.objects.create(
                    title=f"{user_data['name']}'s Property {i+1}",
                    description=f"Beautiful property {i+1} by {user_data['name']}",
                    address=f"{user_data['address']} Unit {i+1}",
                    bhk=2,
                    price=1000 + (i * 500),
                    model_type='apartment',
                    year_built=2020,
                    landlord=profile,
                    is_available=True
                )
                # Add default image
                PropertyImage.objects.create(
                    property=property,
                    image='property_images/default_property.jpg',
                    is_primary=True
                )
            
            messages.success(request, f'Created landlord account and properties for {user_data["username"]}')

        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error creating landlords and properties: {str(e)}')
        return redirect('dashboard')

@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.user.userprofile != booking.tenant:
        messages.error(request, 'You are not authorized to make this payment.')
        return redirect('dashboard')
    if booking.status != 'accepted' and booking.status != 'payment':
        messages.error(request, 'This booking has not been accepted yet.')
        return redirect('dashboard')
    try:
        payment = Payment.objects.get(booking=booking)
        payment.status = 'completed'
        payment.save()
        messages.success(request, 'Payment completed successfully!')
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found.')
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
    return redirect('dashboard')

def reset_landlords_and_properties(request):
    """Delete all landlords and properties, then create akshu, luxx, nethu as landlords, each with one property."""
    from django.contrib.auth.models import User
    from .models import UserProfile, Property, PropertyImage
    from django.contrib import messages
    # Delete all properties and landlords
    Property.objects.all().delete()
    UserProfile.objects.filter(user_type='landlord').delete()
    User.objects.filter(userprofile__user_type='landlord').delete()

    landlords = [
        {
            'username': 'akshu',
            'email': 'akshay@gmail.com',
            'password': 'akshu123',
            'name': 'akshay vikas',
            'phone': '7777755555',
            'address': 'akshu234',
            'property': {
                'title': 'Modern 2BHK Apartment',
                'description': 'Beautiful 2BHK by akshu',
                'address': '123 Main Street, City Center',
                'bhk': 2,
                'price': 45000,
                'model_type': 'new',
                'year_built': 2021
            }
        },
        {
            'username': 'luxx',
            'email': 'laksh@gmail.com',
            'password': 'luxx123',
            'name': 'lakshana sri',
            'phone': '2222244444',
            'address': 'lux@2702',
            'property': {
                'title': 'Luxury 3BHK Villa',
                'description': 'Spacious 3BHK by luxx',
                'address': '456 Oak Avenue, Uptown',
                'bhk': 3,
                'price': 60000,
                'model_type': 'villa',
                'year_built': 2020
            }
        },
        {
            'username': 'nethu',
            'email': 'nethra@gmail.com',
            'password': 'nethu123',
            'name': 'nethra sivakumar',
            'phone': '1111133333',
            'address': 'nethu@71',
            'property': {
                'title': 'Cozy 1BHK Studio',
                'description': 'Cozy studio by nethu',
                'address': '789 Pine Road, Suburb',
                'bhk': 1,
                'price': 25000,
                'model_type': 'studio',
                'year_built': 2019
            }
        }
    ]
    for data in landlords:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['name'].split()[0],
            last_name=' '.join(data['name'].split()[1:])
        )
        profile = UserProfile.objects.create(
            user=user,
            user_type='landlord',
            phone_number=data['phone'],
            address=data['address']
        )
        prop = Property.objects.create(
            title=data['property']['title'],
            description=data['property']['description'],
            address=data['property']['address'],
            bhk=data['property']['bhk'],
            price=data['property']['price'],
            model_type=data['property']['model_type'],
            year_built=data['property']['year_built'],
            landlord=profile,
            is_available=True
        )
        PropertyImage.objects.create(
            property=prop,
            image='property_images/default_property.jpg',
            is_primary=True
        )
        messages.success(request, f'Created landlord {data["username"]} and property {data["property"]["title"]}')
    return redirect('dashboard')

def create_sample_properties(request):
    from django.contrib.auth.models import User
    from .models import UserProfile, Property, PropertyImage, Complaint, Review
    from django.contrib import messages
    import random
    # Get landlords
    landlords = []
    for username in ['akshu', 'luxx', 'nethu']:
        try:
            landlords.append(UserProfile.objects.get(user__username=username))
        except UserProfile.DoesNotExist:
            continue
    if not landlords:
        messages.error(request, 'No landlords found. Please create landlords first.')
        return redirect('dashboard')
    # Delete all properties first
    Property.objects.all().delete()
    # Data for properties
    bhks = [1, 2, 3, 4]
    prices = [20000, 25000, 30000, 35000, 40000, 45000, 50000, 60000]
    titles = [
        'Modern Apartment', 'Luxury Villa', 'Cozy Studio', 'Spacious House',
        'Elegant Flat', 'Urban Condo', 'Classic Loft', 'Family Home',
        'Premium Suite', 'Affordable Living', 'Green Apartment', 'Sunny Villa',
        'Peaceful Studio', 'Grand Mansion', 'Stylish Flat', 'Central Condo',
        'Chic Loft', 'Comfort Home', 'Smart Suite', 'Budget Studio'
    ]
    descriptions = [
        'Beautiful apartment with modern amenities.',
        'Spacious villa with private garden.',
        'Cozy studio perfect for singles.',
        'Large house ideal for families.',
        'Elegant flat with city views.',
        'Urban condo with all facilities.',
        'Classic loft in a prime location.',
        'Family home with backyard.',
        'Premium suite with luxury fittings.',
        'Affordable living in a great area.',
        'Green apartment with eco features.',
        'Sunny villa with pool.',
        'Peaceful studio near park.',
        'Grand mansion with 4 bedrooms.',
        'Stylish flat with modern design.',
        'Central condo close to metro.',
        'Chic loft with open plan.',
        'Comfortable home for families.',
        'Smart suite with automation.',
        'Budget studio for students.'
    ]
    addresses = [
        '123 Main Street, City Center', '456 Oak Avenue, Uptown', '789 Pine Road, Suburb',
        '321 Maple Lane, Downtown', '654 Cedar Street, Riverside', '987 Elm Road, Midtown',
        '111 Willow Way, Parkside', '222 Birch Blvd, Seaside', '333 Aspen Ave, Hilltop',
        '444 Spruce St, Lakeside', '555 Poplar Pl, Countryside', '666 Chestnut Ct, Oldtown',
        '777 Sycamore Dr, Newcity', '888 Redwood Rd, Greenfield', '999 Magnolia Ln, Bluebay',
        '1010 Cypress Cir, Redhill', '1111 Alder Ave, Sunview', '1212 Beech Blvd, Goldpark',
        '1313 Dogwood Dr, Silverlake', '1414 Hawthorn St, Westend'
    ]
    images = [
        'property_images/default_property.jpg',
        'property_images/property1_1.jpg',
        'property_images/property2_1.jpg',
        'property_images/property3_1.jpg',
        'property_images/property4_1.jpg',
        'property_images/property5_1.jpg',
        'property_images/property6_1.jpg',
        'property_images/property7_1.jpg',
        'property_images/property8_1.jpg',
        'property_images/property9_1.jpg',
        'property_images/property10_1.jpg',
    ]
    for i in range(20):
        landlord = landlords[i % len(landlords)]
        bhk = bhks[i % len(bhks)]
        price = prices[i % len(prices)]
        title = f"{titles[i]} {bhk}BHK"
        description = descriptions[i]
        address = addresses[i]
        year_built = 2018 + (i % 7)
        prop = Property.objects.create(
            title=title,
            description=description,
            address=address,
            bhk=bhk,
            price=price,
            model_type=random.choice(['apartment', 'villa', 'studio', 'flat', 'condo', 'house']),
            year_built=year_built,
            landlord=landlord,
            is_available=True
        )
        # Add images
        for img in images[i % len(images):(i % len(images))+1]:
            PropertyImage.objects.create(property=prop, image=img, is_primary=True)
        # Add sample complaint
        Complaint.objects.create(
            property=prop,
            tenant=None,
            title='Sample Complaint',
            description='There is a minor issue with the plumbing.',
        )
        # Add sample review
        Review.objects.create(
            property=prop,
            user=landlord.user,
            rating=random.randint(3,5),
            comment='Great property! Highly recommended.'
        )
    messages.success(request, '20 sample properties with all BHKs, price ranges, images, and correct landlords created!')
    return redirect('property_list')

def setup_system(request):
    """Complete system setup - creates landlords, properties, and ensures all users have profiles"""
    from django.contrib.auth.models import User
    from .models import UserProfile, Property, PropertyImage, Complaint, Review
    from django.contrib import messages
    import random
    
    # Only delete users created by this setup, not all users
    usernames_to_delete = ['akshu', 'luxx', 'nethu', 'aaadi', 'ajju', 'aarna']
    Property.objects.filter(landlord__user__username__in=usernames_to_delete).delete()
    UserProfile.objects.filter(user__username__in=usernames_to_delete).delete()
    User.objects.filter(username__in=usernames_to_delete).delete()
    
    # Create landlords
    landlords_data = [
        {
            'username': 'akshu',
            'email': 'akshay@gmail.com',
            'password': 'akshu123',
            'name': 'akshay vikas',
            'phone': '7777755555',
            'address': 'akshu234'
        },
        {
            'username': 'luxx',
            'email': 'laksh@gmail.com',
            'password': 'luxx123',
            'name': 'lakshana sri',
            'phone': '2222244444',
            'address': 'lux@2702'
        },
        {
            'username': 'nethu',
            'email': 'nethra@gmail.com',
            'password': 'nethu123',
            'name': 'nethra sivakumar',
            'phone': '1111133333',
            'address': 'nethu@71'
        }
    ]
    
    # Create tenants
    tenants_data = [
        {
            'username': 'aaadi',
            'email': 'aadi@gmail.com',
            'password': 'aadi123',
            'name': 'aaditya arun',
            'phone': '23456789',
            'address': 'aadi1122'
        },
        {
            'username': 'ajju',
            'email': 'arjun@gmail.com',
            'password': 'ajju123',
            'name': 'arjun sharma',
            'phone': '9999900000',
            'address': 'ajju5566'
        },
        {
            'username': 'aarna',
            'email': 'aarna@gmail.com',
            'password': 'aarna123',
            'name': 'aarna avyuth',
            'phone': '1111100000',
            'address': 'aarna@26'
        }
    ]
    
    # Create all users and their profiles
    for user_data in landlords_data + tenants_data:
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['name'].split()[0],
            last_name=' '.join(user_data['name'].split()[1:])
        )
        UserProfile.objects.create(
            user=user,
            user_type='landlord' if user_data in landlords_data else 'tenant',
            phone_number=user_data['phone'],
            address=user_data['address']
        )
    
    messages.success(request, 'System has been reset and setup users recreated!')
    return redirect('login')

@login_required
def landlord_dashboard(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'landlord':
        messages.error(request, 'Access denied. Landlord access required.')
        return redirect('home')
    
    # Get all properties owned by this landlord
    properties = Property.objects.filter(landlord=request.user.userprofile)
    
    # Get all bookings for these properties
    bookings = Booking.objects.filter(property__in=properties)
    
    # Get all reviews for these properties
    reviews = Review.objects.filter(property__in=properties)
    
    # Get all complaints for these properties
    complaints = Complaint.objects.filter(property__in=properties)
    
    context = {
        'properties': properties,
        'bookings': bookings,
        'reviews': reviews,
        'complaints': complaints,
    }
    return render(request, 'rental_app/landlord_dashboard.html', context)

@login_required
def landlord_reviews_complaints(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'landlord':
        messages.error(request, 'Access denied. Landlord access required.')
        return redirect('home')
    
    # Get all properties owned by this landlord
    properties = Property.objects.filter(landlord=request.user.userprofile)
    
    # Get all reviews for these properties
    reviews = Review.objects.filter(property__in=properties)
    
    # Get all complaints for these properties
    complaints = Complaint.objects.filter(property__in=properties)
    
    context = {
        'reviews': reviews,
        'complaints': complaints,
    }
    return render(request, 'rental_app/landlord_reviews_complaints.html', context)

@login_required
def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    
    # Check if the user is the landlord of the property
    if not hasattr(request.user, 'userprofile') or request.user.userprofile != complaint.property.landlord:
        messages.error(request, 'You are not authorized to update this complaint.')
        return redirect('property_detail', pk=complaint.property.pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['resolved', 'rejected']:
            complaint.status = new_status
            complaint.save()
            messages.success(request, f'Complaint marked as {new_status}.')
        else:
            messages.error(request, 'Invalid status provided.')
    
    return redirect('property_detail', pk=complaint.property.pk)

@login_required
def submit_review(request, property_pk):
    property = get_object_or_404(Property, pk=property_pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = property
            review.user = request.user.userprofile
            review.save()
            
            # Create notification for the landlord
            Notification.objects.create(
                user=property.landlord.user,
                title='New Review',
                message=f'A new review has been submitted for your property: {property.title}'
            )
            
            messages.success(request, 'Review submitted successfully! The landlord has been notified.')
            return redirect('property_detail', pk=property_pk)
    else:
        form = ReviewForm()
    return render(request, 'rental_app/property_detail.html', {'form': form, 'property': property})
@login_required
def book_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    logger.info(f"Attempting to book property {pk} by user {request.user.username}")
    
    # Check if user is a tenant
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'tenant':
        messages.error(request, 'Only tenants can book properties.')
        return redirect('property_detail', pk=pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create the booking
                    booking = form.save(commit=False)
                    booking.property = property
                    booking.tenant = request.user.userprofile
                    booking.status = 'pending'
                    booking.save()
                    logger.info(f"Created booking {booking.id} for property {property.title}")
                    
                    # Create a payment record
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=property.price,
                        status='pending'
                    )
                    logger.info(f"Created payment record {payment.id} for booking {booking.id}")
                    
                    # Create notification for landlord
                    Notification.objects.create(
                        user=property.landlord.user,
                        title='New Booking Request',
                        message=f'A new booking request has been submitted for your property: {property.title}'
                    )
                    
                    # Add debug message
                    messages.info(request, f'Booking created with ID: {booking.id}')
                
                messages.success(request, 'Booking request submitted successfully! Please wait for landlord approval.')
                return redirect('manage_bookings')
            except Exception as e:
                logger.error(f"Error creating booking: {str(e)}")
                messages.error(request, f'Error creating booking: {str(e)}')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = BookingForm()
    return render(request, 'rental_app/book_property.html', {'form': form, 'property': property})
@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Check if user is the tenant who made the booking
    if request.user.userprofile != booking.tenant:
        messages.error(request, 'You are not authorized to make this payment.')
        return redirect('manage_bookings')
    
    # Check if booking is in the right status
    if booking.status != 'accepted':
        messages.error(request, 'This booking has not been accepted yet.')
        return redirect('manage_bookings')
    
    try:
        # Process payment
        payment = Payment.objects.get(booking=booking)
        payment.status = 'completed'
        payment.transaction_id = f"TXN-{booking.id}-{int(timezone.now().timestamp())}"
        payment.save()
        
        # Create notification for landlord
        Notification.objects.create(
            user=booking.property.landlord.user,
            title='Payment Received',
            message=f'Payment has been received for booking of {booking.property.title}'
        )
        
        messages.success(request, 'Payment completed successfully!')
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found.')
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
    
    return redirect('manage_bookings')
@login_required
def manage_bookings(request):
    user_profile = request.user.userprofile
    logger.info(f"Managing bookings for user {request.user.username} (type: {user_profile.user_type})")
    
    try:
        if user_profile.user_type == 'landlord':
            # Get all bookings for properties owned by this landlord
            bookings = Booking.objects.filter(
                property__landlord=user_profile
            ).select_related(
                'property',
                'tenant',
                'tenant__user'
            ).prefetch_related(
                'payment_set'  # Make sure to prefetch payments
            ).order_by('-created_at')
            
            # Debug information
            logger.info(f"Found {bookings.count()} bookings for landlord {request.user.username}")
            
        else:  # tenant view
            bookings = Booking.objects.filter(
                tenant=user_profile
            ).select_related(
                'property',
                'property__landlord',
                'property__landlord__user'
            ).prefetch_related(
                'payment_set'  # Make sure to prefetch payments
            ).order_by('-created_at')
            
            logger.info(f"Found {bookings.count()} bookings for tenant {request.user.username}")
            
    except Exception as e:
        logger.error(f"Error in manage_bookings: {str(e)}")
        messages.error(request, f'Error loading bookings: {str(e)}')
        bookings = []
    
    # Add payment information to each booking
    for booking in bookings:
        try:
            booking.payment = Payment.objects.get(booking=booking)
        except Payment.DoesNotExist:
            booking.payment = None
    
    context = {
        'bookings': bookings,
        'has_bookings': bookings.exists(),
        'user_type': user_profile.user_type
    }
    return render(request, 'rental_app/manage_bookings.html', context),

@login_required
def manage_properties(request):
    """View for landlords to manage their properties"""
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, 'Your account is missing a profile. Please log in again.')
        return redirect('login')
    
    user_profile = request.user.userprofile

    if user_profile.user_type != 'landlord':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    properties = Property.objects.filter(landlord=user_profile)
    context = {
        'properties': properties,
    } 
    return render(request, 'rental_app/manage_properties.html', context)
@login_required
def manage_bookings(request):
    user_profile = request.user.userprofile
    logger.info(f"Managing bookings for user {request.user.username} (type: {user_profile.user_type})")
    
    try:
        if user_profile.user_type == 'landlord':
            # Get all bookings for properties owned by this landlord
            bookings = Booking.objects.filter(
                property__landlord=user_profile
            ).select_related(
                'property',
                'tenant',
                'tenant__user'
            ).prefetch_related(
                'payment_set'  # Make sure to prefetch payments
            ).order_by('-created_at')
            
            # Debug information
            logger.info(f"Found {bookings.count()} bookings for landlord {request.user.username}")
            
        else:  # tenant view
            bookings = Booking.objects.filter(
                tenant=user_profile
            ).select_related(
                'property',
                'property__landlord',
                'property__landlord__user'
            ).prefetch_related(
                'payment_set'  # Make sure to prefetch payments
            ).order_by('-created_at')
            
            logger.info(f"Found {bookings.count()} bookings for tenant {request.user.username}")
            
    except Exception as e:
        logger.error(f"Error in manage_bookings: {str(e)}")
        messages.error(request, f'Error loading bookings: {str(e)}')
        bookings = []
    
    # Add payment information to each booking
    for booking in bookings:
        try:
            booking.payment = Payment.objects.get(booking=booking)
        except Payment.DoesNotExist:
            booking.payment = None
    
    context = {
        'bookings': bookings,
        'has_bookings': bookings.exists(),
        'user_type': user_profile.user_type
    }
    # Remove the trailing comma here - this was causing the tuple issue
    return render(request, 'rental_app/manage_bookings.html', context)
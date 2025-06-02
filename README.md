# Rental Property Management System

A comprehensive online rental property management system built with Django.

## Features

- User Registration and Login (Landlord and Tenant)
- Property Management
- Booking System
- Payment Processing
- Complaint Management
- Property Filtering (BHK and Price)
- Image Upload for Properties
- Notification System

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Register as either a Landlord or Tenant
2. Landlords can:
   - Add properties
   - View complaints
   - Accept payments
3. Tenants can:
   - View properties
   - Book properties
   - Make payments
   - Submit complaints 
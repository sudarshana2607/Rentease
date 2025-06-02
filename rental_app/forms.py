from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Property, PropertyImage, Booking, Complaint, Review
from django.utils import timezone

class UserRegistrationForm(UserCreationForm):
    USER_TYPES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    )
    
    user_type = forms.ChoiceField(choices=USER_TYPES)
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'phone_number', 'address')

class PropertyForm(forms.ModelForm):
    images = forms.ImageField(required=False)
    
    class Meta:
        model = Property
        fields = ('title', 'description', 'address', 'bhk', 'price', 'model_type', 'year_built')
        exclude = ['landlord']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ('image', 'is_primary')

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('start_date', 'end_date')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date < timezone.now().date():
                raise forms.ValidationError("Start date cannot be in the past")
            if end_date <= start_date:
                raise forms.ValidationError("End date must be after start date")

        return cleaned_data

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('title', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PropertySearchForm(forms.Form):
    bhk = forms.ChoiceField(choices=Property.BHK_CHOICES, required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    model_type = forms.ChoiceField(choices=[('', 'Any')] + Property.MODEL_TYPE_CHOICES, required=False, label='Model Type')
    year_built = forms.IntegerField(required=False, min_value=1800, label='Year Built')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'rating': forms.Select()
        } 
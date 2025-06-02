from django.contrib import admin
from .models import UserProfile, Property, PropertyImage, Booking, Payment, Complaint, Notification, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'created_at')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'landlord', 'bhk', 'price', 'is_available', 'created_at')
    list_filter = ('bhk', 'is_available', 'created_at')
    search_fields = ('title', 'description', 'address')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__title', 'tenant__user__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_date')
    search_fields = ('booking__property__title', 'transaction_id')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'title', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'property__title', 'tenant__user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('property__title', 'user__user__username', 'comment')

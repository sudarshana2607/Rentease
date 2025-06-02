from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/add/', views.add_property, name='add_property'),
    path('properties/<int:pk>/book/', views.book_property, name='book_property'),
    path('properties/<int:property_pk>/submit-review/', views.submit_review, name='submit_review'),
    path('properties/<int:property_pk>/submit-complaint/', views.submit_complaint, name='submit_complaint'),
    path('complaints/<int:complaint_id>/update-status/', views.update_complaint_status, name='update_complaint_status'),
    path('manage-bookings/', views.manage_bookings, name='manage_bookings'),
    path('bookings/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    path('bookings/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('bookings/<int:booking_id>/payment/', views.process_payment, name='process_payment'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('create-landlords/', views.create_landlords, name='create_landlords'),
    path('create-tenants/', views.create_tenants, name='create_tenants'),
    path('create-new-landlords/', views.create_new_landlords, name='create_new_landlords'),
    path('reset-landlords-properties/', views.reset_landlords_and_properties, name='reset_landlords_and_properties'),
    path('create-sample-properties/', views.create_sample_properties, name='create_sample_properties'),
    path('setup-system/', views.setup_system, name='setup_system'),
    path('landlord-dashboard/', views.landlord_dashboard, name='landlord_dashboard'),
    path('landlord-reviews-complaints/', views.landlord_reviews_complaints, name='landlord_reviews_complaints'),

   
] 
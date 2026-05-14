from django.contrib import admin
from django.urls import path
from chipta.views import search_flights, seed_data, book_flight, my_bookings, register_user, login_user, create_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/flights/', search_flights, name='search_flights'),
    path('api/book/', book_flight, name='book_flight'),
    path('api/my-bookings/', my_bookings, name='my_bookings'),
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),
    path('api/seed/', seed_data, name='seed_data'),
    path('api/create-admin/', create_admin, name='create_admin'),
]
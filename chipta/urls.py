from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('flights/', views.flight_list, name='flight_list'),
    path('book/<int:flight_id>/', views.book_ticket, name='book_ticket'),
    path('tickets/', views.ticket_list, name='ticket_list'),
]
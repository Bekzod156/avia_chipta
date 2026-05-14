from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Flight, Airport, Passenger, Ticket
from django.utils import timezone
from decimal import Decimal
import datetime
import json
from django.views.decorators.csrf import csrf_exempt

# --- Flight & Booking APIs ---

def search_flights(request):
    """ FrontEnd uchun reyslarni qidirish API """
    from_city = request.GET.get('from', '')
    to_city = request.GET.get('to', '')
    
    flights = Flight.objects.all()
    
    if from_city:
        flights = flights.filter(departure_airport__city__icontains=from_city)
    if to_city:
        flights = flights.filter(arrival_airport__city__icontains=to_city)
        
    data = []
    for flight in flights:
        data.append({
            'id': flight.id,
            'flight_number': flight.flight_number,
            'from_city': flight.departure_airport.city,
            'from_code': flight.departure_airport.code,
            'to_city': flight.arrival_airport.city,
            'to_code': flight.arrival_airport.code,
            'departure_time': flight.departure_time.strftime('%Y-%m-%d %H:%M'),
            'price': float(flight.price),
            'available_seats': flight.available_seats(),
        })
    
    return JsonResponse(data, safe=False)

@csrf_exempt
def book_flight(request):
    """ Chipta bron qilish API """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            flight_id = data.get('flight_id')
            passport = data.get('passport_number')
            phone = data.get('phone_number')
            seat = data.get('seat_number')
            user_id = data.get('user_id') # Agar tizimga kirgan bo'lsa

            flight = Flight.objects.get(id=flight_id)
            
            # Yo'lovchini qidirish yoki yaratish
            passenger, created = Passenger.objects.get_or_create(
                passport_number=passport,
                defaults={'phone_number': phone}
            )

            # Chipta yaratish
            ticket = Ticket.objects.create(
                flight=flight,
                passenger=passenger,
                seat_number=seat,
                status='pending',
                user_id=user_id if user_id else None
            )

            return JsonResponse({
                'status': 'success',
                'message': f'Chipta muvaffaqiyatli bron qilindi!',
                'ticket_id': ticket.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def my_bookings(request):
    """ Foydalanuvchining bron qilgan chiptalari API """
    passport = request.GET.get('passport', '')
    user_id = request.GET.get('user_id', '')

    if user_id:
        tickets = Ticket.objects.filter(user_id=user_id)
    elif passport:
        tickets = Ticket.objects.filter(passenger__passport_number=passport)
    else:
        return JsonResponse({'status': 'error', 'message': 'Passport yoki User ID kerak'}, status=400)
    
    data = []
    for ticket in tickets:
        data.append({
            'id': ticket.id,
            'flight_number': ticket.flight.flight_number,
            'from': ticket.flight.departure_airport.city,
            'to': ticket.flight.arrival_airport.city,
            'date': ticket.flight.departure_time.strftime('%Y-%m-%d %H:%M'),
            'seat': ticket.seat_number,
            'status': ticket.status,
            'price': float(ticket.flight.price)
        })
    return JsonResponse(data, safe=False)

# --- Auth APIs ---

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            passport = data.get('passport_number')
            phone = data.get('phone_number')
            password = data.get('password')

            if User.objects.filter(username=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Bu email allaqachon ro\'yxatdan o\'tgan!'}, status=400)

            user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
            Passenger.objects.create(user=user, passport_number=passport, phone_number=phone)

            return JsonResponse({'status': 'success', 'message': 'Ro\'yxatdan o\'tish muvaffaqiyatli yakunlandi!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                passenger = Passenger.objects.filter(user=user).first()
                return JsonResponse({
                    'status': 'success',
                    'user': {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'passport_number': passenger.passport_number if passenger else 'ADMIN',
                        'phone_number': passenger.phone_number if passenger else 'ADMIN'
                    }
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Email yoki parol xato!'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def seed_data(request):
    """ Bazaga namunaviy ma'lumotlar qo'shish """
    tas, _ = Airport.objects.get_or_create(code='TAS', defaults={'name': 'Tashkent International', 'city': 'Toshkent', 'country': 'Oʻzbekiston'})
    ist, _ = Airport.objects.get_or_create(code='IST', defaults={'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkiya'})
    dxb, _ = Airport.objects.get_or_create(code='DXB', defaults={'name': 'Dubai International', 'city': 'Dubay', 'country': 'BAA'})
    
    Flight.objects.get_or_create(flight_number='HY-271', defaults={'departure_airport': tas, 'arrival_airport': ist, 'departure_time': timezone.now() + datetime.timedelta(days=2), 'arrival_time': timezone.now() + datetime.timedelta(days=2, hours=4), 'price': Decimal('3500000.00')})
    Flight.objects.get_or_create(flight_number='EK-701', defaults={'departure_airport': tas, 'arrival_airport': dxb, 'departure_time': timezone.now() + datetime.timedelta(days=3), 'arrival_time': timezone.now() + datetime.timedelta(days=3, hours=3), 'price': Decimal('4200000.00')})
    
    return JsonResponse({'status': 'success', 'message': 'Ma\'lumotlar yangilandi!'})
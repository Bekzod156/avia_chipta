from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flight, Ticket, Passenger
from .forms import RegisterForm, LoginForm, TicketForm
import re
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Flight, Ticket, Passenger
from .forms import TicketForm

@login_required(login_url='login')
def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    passenger = get_object_or_404(Passenger, user=request.user)

    if request.method == 'POST':
        t_form = TicketForm(request.POST)
        passport_input = request.POST.get('passport_check', '').strip().upper()

        # Format tekshiruvi: 2 harf + 7 raqam
        passport_pattern = re.compile(r'^[A-Z]{2}\d{7}$')

        if not passport_pattern.match(passport_input):
            messages.error(request, "❌ Xatolik yuz berdi! Pasport seriyasi noto'g'ri formatda (masalan: AD1234567)")
            return render(request, 'book_ticket.html', {'flight': flight, 't_form': t_form})

        if passport_input != passenger.passport_number.strip().upper():
            messages.error(request, "❌ Xatolik yuz berdi! Pasport seriyasi sizning ma'lumotlaringizga mos kelmadi.")
            return render(request, 'book_ticket.html', {'flight': flight, 't_form': TicketForm()})

        if flight.available_seats <= 0:
            messages.error(request, "❌ Kechirasiz, bu reysda bo'sh o'rindiqlar qolmagan!")
            return render(request, 'book_ticket.html', {'flight': flight, 't_form': TicketForm()})

        if t_form.is_valid():
            ticket = t_form.save(commit=False)
            ticket.flight = flight
            ticket.passenger = passenger
            ticket.status = 'pending'
            ticket.save()

            messages.success(request,
                "✅ Chipta muvaffaqiyatli buyurtma berildi! "
                "2 kun ichida bizning kassaga kelib pulni to'lashingiz mumkin."
            )
            return redirect('flight_list')

        messages.error(request, "❌ Xatolik yuz berdi! Formani to'g'ri to'ldiring.")

    else:
        t_form = TicketForm()

    return render(request, 'book_ticket.html', {
        'flight': flight,
        't_form': t_form
    })


# 1. Bosh sahifa
def home(request):
    return render(request, 'home.html')


# 2. Ro'yxatdan o'tish
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        # User yaratish
        user = User.objects.create_user(
            username=data['email'],  # email = username
            email=data['email'],
            password=data['password1'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        # Passenger yaratish
        Passenger.objects.create(
            user=user,
            passport_number=data['passport_number'],
            phone_number=data['phone_number'],
        )
        login(request, user)
        messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz!")
        return redirect('home')

    return render(request, 'register.html', {'form': form})


# 3. Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        user = authenticate(request, username=data['email'], password=data['password'])
        if user:
            login(request, user)
            messages.success(request, "Xush kelibsiz!")
            return redirect('home')
        else:
            messages.error(request, "Email yoki parol noto'g'ri!")

    return render(request, 'login.html', {'form': form})


# 4. Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# 5. Reyslar ro'yxati
@login_required(login_url='login')
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'flight_list.html', {'flights': flights})


# 6. Chipta bron qilish
@login_required(login_url='login')
def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    try:
        passenger = Passenger.objects.get(user=request.user)
    except Passenger.DoesNotExist:
        messages.error(request, "❌ Profilingiz topilmadi. Iltimos qayta ro'yxatdan o'ting.")
        return redirect('register')

    # ✅ available_seats ni view'da hisoblaymiz
    available_seats = flight.available_seats()

    if request.method == 'POST':
        t_form = TicketForm(request.POST)
        passport_input = request.POST.get('passport_check', '').strip().upper()
        passport_pattern = re.compile(r'^[A-Z]{2}\d{7}$')

        if not passport_pattern.match(passport_input):
            messages.error(request, "❌ Xatolik yuz berdi! Pasport seriyasi noto'g'ri formatda (masalan: AD1234567)")
            return render(request, 'book_ticket.html',
                          {'flight': flight, 't_form': t_form, 'available_seats': available_seats})

        if passport_input != passenger.passport_number.strip().upper():
            messages.error(request, "❌ Xatolik yuz berdi! Pasport seriyasi sizning ma'lumotlaringizga mos kelmadi.")
            return render(request, 'book_ticket.html',
                          {'flight': flight, 't_form': TicketForm(), 'available_seats': available_seats})

        if available_seats <= 0:
            messages.error(request, "❌ Kechirasiz, bu reysda bo'sh o'rindiqlar qolmagan!")
            return render(request, 'book_ticket.html',
                          {'flight': flight, 't_form': TicketForm(), 'available_seats': available_seats})

        if t_form.is_valid():
            ticket = t_form.save(commit=False)
            ticket.flight = flight
            ticket.passenger = passenger
            ticket.status = 'pending'
            ticket.save()
            messages.success(request,
                             "✅ Chipta muvaffaqiyatli buyurtma berildi! "
                             "2 kun ichida bizning kassaga kelib pulni to'lashingiz mumkin."
                             )
            return redirect('flight_list')

        messages.error(request, "❌ Xatolik yuz berdi! Formani to'g'ri to'ldiring.")

    else:
        t_form = TicketForm()

    return render(request, 'book_ticket.html', {
        'flight': flight,
        't_form': t_form,
        'available_seats': available_seats,  # ✅ template'ga uzatiladi
    })
@login_required(login_url='login')
def ticket_list(request):
    passenger = get_object_or_404(Passenger, user=request.user)
    tickets = Ticket.objects.filter(passenger=passenger).order_by('-booking_date')
    return render(request, 'ticket_list.html', {'tickets': tickets})
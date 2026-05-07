from django.db import models


class Airport(models.Model):
    """ Aeroportlar va manzillar modeli """
    name = models.CharField(max_length=150, verbose_name="Aeroport nomi")
    code = models.CharField(max_length=10, unique=True, verbose_name="Aeroport kodi (masalan, TAS)")
    city = models.CharField(max_length=100, verbose_name="Shahar")
    country = models.CharField(max_length=100, verbose_name="Davlat")

    def __str__(self):
        return f"{self.city} ({self.code})"

    class Meta:
        verbose_name = "Aeroport"
        verbose_name_plural = "Aeroportlar"

class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True, verbose_name="Reys raqami")
    departure_airport = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE,
                                          verbose_name="Uchish aeroporti")
    arrival_airport = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE,
                                        verbose_name="Qo'nish aeroporti")
    departure_time = models.DateTimeField(verbose_name="Uchish vaqti")
    arrival_time = models.DateTimeField(verbose_name="Qo'nish vaqti")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Chipta narxi ($)")
    total_seats = models.PositiveIntegerField(default=150, verbose_name="Umumiy o'rindiqlar soni")

    # ✅ Bron qilingan chiptalardan avtomatik hisoblaydi
    def available_seats(self):
        from chipta.models import Ticket
        booked = Ticket.objects.filter(flight=self).exclude(status='cancelled').count()
        return self.total_seats - booked
    def __str__(self):
        return f"{self.flight_number}: {self.departure_airport.city} -> {self.arrival_airport.city}"

    class Meta:
        verbose_name = "Reys"
        verbose_name_plural = "Reyslar"
from django.contrib.auth.models import User
from django.db import models

class Passenger(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Foydalanuvchi",
        null=True,   # ✅ shu qo'shiladi
        blank=True   # ✅ shu qo'shiladi
    )
    passport_number = models.CharField(max_length=20, unique=True, verbose_name="Pasport raqami")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqami")

    class Meta:
        verbose_name = "Yo'lovchi"
        verbose_name_plural = "Yo'lovchilar"


class Ticket(models.Model):
    """ Chipta va bron qilish modeli """
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda (Bron qilingan)'),
        ('paid', 'To\'langan'),
        ('cancelled', 'Bekor qilingan'),
    )

    # Agar saytga kirgan foydalanuvchi o'ziga yoki boshqaga chipta olayotgan bo'lsa
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name="Foydalanuvchi (Sayt a'zosi)")
    flight = models.ForeignKey(Flight, related_name='tickets', on_delete=models.CASCADE, verbose_name="Reys")
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, verbose_name="Yo'lovchi")
    seat_number = models.CharField(max_length=10, verbose_name="O'rindiq raqami")
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name="Bron qilingan sana")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")

    def __str__(self):
        return f"Chipta #{self.id} - {self.flight.flight_number} - {self.passenger.last_name}"

    class Meta:
        verbose_name = "Chipta"
        verbose_name_plural = "Chiptalar"

# Create your models here.

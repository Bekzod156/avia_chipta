from django.contrib import admin
from .models import Airport,Flight,Ticket,Passenger

# Register your models here.
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Passenger)

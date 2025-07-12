from django.contrib import admin
from .models import Event, EventRegistration, Announcement

admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(Announcement)

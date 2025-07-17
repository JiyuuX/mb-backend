from django.contrib import admin
from .models import Event, Ticket

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ('user', 'user_full_name', 'purchased_at', 'code')
    can_delete = False
    fields = ('user', 'user_full_name', 'purchased_at', 'code')
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def user_full_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.first_name:
            return obj.user.first_name
        elif obj.user.last_name:
            return obj.user.last_name
        else:
            return obj.user.username
    user_full_name.short_description = 'Ad Soyad'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'city', 'date', 'time', 'ticket_price', 'capacity', 'ticket_count')
    list_filter = ('date', 'is_approved', 'venue', 'city')
    search_fields = ('name', 'venue', 'description', 'city')
    readonly_fields = ('created_at',)
    
    inlines = [TicketInline]
    
    def ticket_count(self, obj):
        return obj.ticket_set.count()
    ticket_count.short_description = 'Satılan Bilet'
    ticket_count.admin_order_field = 'ticket__count'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_full_name', 'event', 'purchased_at', 'code', 'event_venue', 'event_date')
    list_filter = ('event', 'purchased_at', 'event__venue')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'event__name', 'code')
    readonly_fields = ('purchased_at', 'code')
    
    def user_full_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.first_name:
            return obj.user.first_name
        elif obj.user.last_name:
            return obj.user.last_name
        else:
            return obj.user.username
    user_full_name.short_description = 'Ad Soyad'
    user_full_name.admin_order_field = 'user__first_name'
    
    def event_venue(self, obj):
        return obj.event.venue
    event_venue.short_description = 'Mekan'
    event_venue.admin_order_field = 'event__venue'
    
    def event_date(self, obj):
        return f"{obj.event.date} {obj.event.time}"
    event_date.short_description = 'Etkinlik Tarihi'
    event_date.admin_order_field = 'event__date'

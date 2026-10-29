from django.contrib import admin
from .models import Lead, Event, Organizer

@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'yandex_email')
    search_fields = ('name', 'slug')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'date', 'direction', 'is_active')
    list_filter = ('organizer', 'direction', 'is_active')
    search_fields = ('title',)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'direction', 'event', 'created_at')
    list_filter = ('direction', 'created_at')
    search_fields = ('name', 'contact', 'event__title')
    readonly_fields = ('created_at',)
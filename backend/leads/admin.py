from django.contrib import admin
from .models import Lead, Event, Organizer, SiteSettings

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
    
    
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('require_email_verification',)
    
    def has_add_permission(self, request):
        # Запрещаем создавать больше одной записи
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удалять единственную запись настроек
        return False
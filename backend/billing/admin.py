from django.contrib import admin
from django.utils.html import format_html
from .models import Plan, Subscription
from django.utils.safestring import mark_safe

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'max_events', 'has_calendar_sync', 'has_waitlist')
    list_editable = ('price', 'max_events', 'has_calendar_sync', 'has_waitlist')
    prepopulated_fields = {'slug': ('name',)} # Автоматически заполняет slug из названия
    search_fields = ('name', 'slug')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'price')
        }),
        ('Возможности тарифа', {
            'fields': ('max_events', 'has_calendar_sync', 'has_waitlist'),
            'description': 'Укажите 0 в поле "Макс. событий" для безлимита.'
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status_badge', 'expires_at', 'payment_id')
    list_filter = ('plan', 'is_active')
    search_fields = ('user__username', 'user__email', 'payment_id')
    readonly_fields = ('payment_id',)
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Подписка', {
            'fields': ('plan', 'is_active', 'expires_at')
        }),
        ('Платеж', {
            'fields': ('payment_id',),
            'classes': ('collapse',) # Скрываем блок, чтобы не мешал
        }),
    )

    def status_badge(self, obj):
        if obj.is_valid:
            return mark_safe('<span style="background-color: #e8f5e9; color: #2e7d32; padding: 3px 8px; border-radius: 10px; font-weight: bold;">✅ Активна</span>')
        elif obj.plan and obj.plan.price == 0:
            return mark_safe('<span style="background-color: #e3f2fd; color: #1565c0; padding: 3px 8px; border-radius: 10px;">Бесплатный</span>')
        else:
            return mark_safe('<span style="background-color: #ffebee; color: #c62828; padding: 3px 8px; border-radius: 10px;">❌ Не активна</span>')
    
    status_badge.short_description = "Статус"

    # Добавляем действие для ручного продления подписки
    actions = ['extend_30_days']

    def extend_30_days(self, request, queryset):
        """Массовое продление подписок на 30 дней (удобно для ручных оплат)"""
        count = 0
        for sub in queryset:
            if sub.plan and sub.plan.price > 0:
                sub.extend(30)
                count += 1
        self.message_user(request, f"Подписки продлены на 30 дней для {count} пользователей.")
    
    extend_30_days.short_description = "Продлить выбранные подписки на 30 дней"
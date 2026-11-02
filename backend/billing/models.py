from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Plan(models.Model):
    """Тарифные планы (Бесплатный, Профи, Бизнес)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена (руб/мес)")
    max_events = models.IntegerField(default=1, verbose_name="Макс. событий (0 = безлимит)")
    has_calendar_sync = models.BooleanField(default=False, verbose_name="Синхронизация с календарем")
    has_waitlist = models.BooleanField(default=False, verbose_name="Лист ожидания")
    
    def __str__(self):
        return self.name

class Subscription(models.Model):
    """Активная подписка пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    payment_id = models.CharField(max_length=100, blank=True, verbose_name="ID платежа в ЮKassa")

    @property
    def is_valid(self):
        """Проверяет, активна ли подписка (с учетом даты)"""
        if self.plan and self.plan.price == 0:
            return True # Бесплатный тариф всегда активен
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            self.is_active = False
            self.save()
            return False
        return True

    def extend(self, days=30):
        """Продлевает подписку на N дней"""
        if self.expires_at and self.expires_at > timezone.now():
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = timezone.now() + timedelta(days=days)
        self.is_active = True
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'Нет плана'}"
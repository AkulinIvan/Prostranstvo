from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .calendar_service import sync_event_to_yandex
import uuid

class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    bio = models.TextField(blank=True)
    directions_data = models.JSONField(default=list, blank=True)
    yandex_email = models.EmailField(blank=True)
    yandex_app_password = models.CharField(max_length=200, blank=True)
    yandex_calendar_name = models.CharField(max_length=100, default="Мой календарь")
    
    guarantee_text = models.TextField(blank=True, default="Мы не спамим. Ваши данные защищены.")
    privacy_policy_url = models.URLField(blank=True)
    offer_url = models.URLField(blank=True)
    
    # Автосохранение
    last_saved_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    TYPE_CHOICES = (
        ('open', 'Открытая запись'),
        ('request', 'Запрос на расчет'),
    )
    
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    direction = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='open')
    is_active = models.BooleanField(default=True)
    min_people = models.IntegerField(default=3)
    is_confirmed = models.BooleanField(default=False)
    reminders_sent = models.BooleanField(default=False)
    yandex_uid = models.CharField(max_length=200, blank=True, null=True)
    
    # Пункты 9, 16
    tags = models.CharField(max_length=200, blank=True, verbose_name="Теги (через запятую)")
    view_count = models.IntegerField(default=0, verbose_name="Просмотры")

    @property
    def lead_count(self):
        return self.leads.count()
    
    @property
    def is_full(self):
        return self.lead_count >= self.min_people and self.is_confirmed

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%d.%m %H:%M')})"

class Lead(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('invited', 'Приглашен'),
        ('accepted', 'Принял'),
        ('declined', 'Отказался'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='leads', null=True, blank=True)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    direction = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Пункты для расчета
    guests_count = models.IntegerField(null=True, blank=True)
    budget = models.CharField(max_length=100, blank=True)
    wishes = models.TextField(blank=True)
    
    # Пункт 10: Waitlist
    is_waitlist = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} -> {self.event.title if self.event else 'Общая заявка'}"

class Contact(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.contact})"

class Review(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='reviews')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    author_name = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.IntegerField(default=5)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author_name} - {self.rating}★"

# Сигналы
@receiver(post_save, sender=Event)
def event_saved(sender, instance, created, **kwargs):
    if getattr(instance, '_skip_yandex_sync', False):
        return
    if instance.is_active and instance.organizer.yandex_app_password:
        sync_event_to_yandex(instance, action='create' if created else 'update')

@receiver(post_delete, sender=Event)
def event_deleted(sender, instance, **kwargs):
    if instance.organizer.yandex_app_password:
        sync_event_to_yandex(instance, action='delete')

@receiver(post_save, sender=Lead)
def add_contact_to_base(sender, instance, created, **kwargs):
    if created and instance.event:
        Contact.objects.get_or_create(
            contact=instance.contact,
            defaults={'name': instance.name, 'organizer': instance.event.organizer}
        )
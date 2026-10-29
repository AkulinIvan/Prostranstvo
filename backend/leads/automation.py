from django.core.mail import send_mail
from django.conf import settings
from .models import Event
from datetime import timedelta
from django.utils import timezone

def check_groups_and_notify():
    now = timezone.now()
    
    # 1. Проверка набора групп за 2 дня
    upcoming = Event.objects.filter(is_active=True, is_confirmed=False, date__gte=now, date__lte=now + timedelta(days=2))
    for event in upcoming:
        if event.lead_count >= event.min_people:
            event.is_confirmed = True
            event.save()
            send_mail(
                f'✅ Группа набрана: {event.title}',
                f'На "{event.title}" ({event.date.strftime("%d.%m %H:%M")}) набралось {event.lead_count} чел. Группа состоится!',
                settings.DEFAULT_FROM_EMAIL, [event.organizer.user.email], fail_silently=True
            )

    # 2. Рассылка напоминаний за 24 часа
    tomorrow = Event.objects.filter(is_active=True, is_confirmed=True, reminders_sent=False, date__gte=now, date__lte=now + timedelta(days=1))
    for event in tomorrow:
        for lead in event.leads.all():
            if '@' in lead.contact:
                send_mail(
                    f'Напоминание: {event.title}',
                    f'Привет, {lead.name}!\nЗавтра в {event.date.strftime("%H:%M")} ждем вас на "{event.title}" по адресу: {event.location}.',
                    settings.DEFAULT_FROM_EMAIL, [lead.contact], fail_silently=True
                )
        event.reminders_sent = True
        event.save()
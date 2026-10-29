import caldav
from datetime import timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

def sync_event_to_yandex(event, action='create'):
    org = event.organizer
    if not org.yandex_email or not org.yandex_app_password:
        print("⚠️ Календарь не настроен для организатора", org.name)
        return

    try:
        with caldav.DAVClient(
            url="https://caldav.yandex.ru/",
            username=org.yandex_email,
            password=org.yandex_app_password
        ) as client:
            principal = client.principal()
            
            try:
                calendar = principal.calendar(name=org.yandex_calendar_name)
                print(f"✅ Подключено к календарю: {org.yandex_calendar_name}")
            except Exception as e:
                print(f"⚠️ Календарь {org.yandex_calendar_name} не найден, беру первый доступный: {e}")
                calendars = principal.calendars()
                if not calendars:
                    print("❌ Нет доступных календарей")
                    return
                calendar = calendars[0]
            
            uid = f"event-{event.id}@team-platform.ru"
            
            existing = None
            try:
                existing = calendar.event_by_url(f"{calendar.url}{uid}.ics")
            except caldav.error.NotFoundError:
                pass

            if action == 'delete':
                if existing: existing.delete()
                print(f"🗑️ Событие {event.id} удалено из календаря")
                return

            if action in ['create', 'update']:
                # Убедимся, что дата с часовым поясом (aware datetime)
                if event.date.tzinfo is None:
                    local_tz = pytz.timezone('Asia/Krasnoyarsk')
                    event_date = local_tz.localize(event.date)
                else:
                    event_date = event.date
                
                utc_dt = event_date.astimezone(pytz.UTC)
                dt_start = utc_dt.strftime('%Y%m%dT%H%M%SZ')
                dt_end = (utc_dt + timedelta(hours=2)).strftime('%Y%m%dT%H%M%SZ')
                
                # Убираем возможные переносы строк в описании, чтобы не сломать формат
                safe_desc = event.description.replace('\n', ' ').replace('\r', '') if event.description else ''
                safe_title = event.title.replace('\n', ' ')
                safe_loc = event.location.replace('\n', ' ') if event.location else ''
                
                ical = (
                    "BEGIN:VCALENDAR\r\n"
                    "VERSION:2.0\r\n"
                    "PRODID:-//TeamPlatform//RU\r\n"
                    "BEGIN:VEVENT\r\n"
                    f"UID:{uid}\r\n"
                    f"DTSTART:{dt_start}\r\n"
                    f"DTEND:{dt_end}\r\n"
                    f"SUMMARY:{safe_title}\r\n"
                    f"DESCRIPTION:{safe_desc}\r\n"
                    f"LOCATION:{safe_loc}\r\n"
                    "STATUS:CONFIRMED\r\n"
                    "END:VEVENT\r\n"
                    "END:VCALENDAR\r\n"
                )
                
                if existing:
                    existing.data = ical
                    existing.save()
                    print(f"🔄 Событие {event.id} обновлено в календаре")
                else:
                    calendar.save_event(ical)
                    print(f"✅ Событие {event.id} создано в календаре")
                    # Сохраняем UID в базу
                    event.yandex_uid = uid
                    event._skip_yandex_sync = True
                    event.save()

    except Exception as e:
        print("\n" + "="*50)
        print(f"❌ ОШИБКА ЯНДЕКС КАЛЕНДАРЯ: {e}")
        print("="*50 + "\n")
        logger.error(f"CalDAV Error: {e}")
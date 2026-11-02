import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email_from_organizer(organizer, subject, message, recipient_list):
    """
    Отправляет письмо от имени организатора.
    Если у организатора не настроен SMTP, использует общую почту платформы.
    """
    # Проверяем, настроен ли SMTP у организатора
    if organizer.smtp_host and organizer.smtp_user and organizer.smtp_password:
        return _send_via_organizer_smtp(organizer, subject, message, recipient_list)
    else:
        # Fallback: отправляем через общую почту (как раньше)
        return _send_via_platform_smtp(subject, message, recipient_list)

def _send_via_organizer_smtp(organizer, subject, message, recipient_list):
    """Отправка через SMTP организатора"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{organizer.name} <{organizer.smtp_user}>"
        msg['To'] = ", ".join(recipient_list)
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        if organizer.smtp_use_ssl:
            server = smtplib.SMTP_SSL(organizer.smtp_host, organizer.smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(organizer.smtp_host, organizer.smtp_port, timeout=10)
            server.starttls()

        server.login(organizer.smtp_user, organizer.smtp_password)
        server.sendmail(organizer.smtp_user, recipient_list, msg.as_string())
        server.quit()
        
        logger.info(f"✅ Письмо отправлено от {organizer.smtp_user} для {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка отправки через SMTP организатора {organizer.name}: {e}")
        # Если не удалось через его SMTP, пробуем через общую почту
        return _send_via_platform_smtp(subject, message, recipient_list)

def _send_via_platform_smtp(subject, message, recipient_list):
    """Отправка через общую почту платформы (fallback)"""
    try:
        from django.core.mail import send_mail
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info(f"✅ Письмо отправлено через платформу для {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка отправки через платформу: {e}")
        return False
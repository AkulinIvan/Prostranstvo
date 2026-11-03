from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db import transaction
from django.db.models import F
import re

from billing.models import Plan, Subscription
from .models import Contact, Event, Lead, Organizer, Review, SiteSettings
from .serializers import EventSerializer, LeadSerializer, ReviewSerializer
from .email_utils import send_email_from_organizer


class IsOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'organizer')

    def can_create_event(user):
        if getattr(user.organizer, 'is_free_forever', False):
            return True
        try:
            sub = user.subscription
            if not sub.is_valid:
                return False
            if sub.plan.max_events == 0:
                return True
            current_count = user.organizer.events.filter(is_active=True).count()
            return current_count < sub.plan.max_events
        except Subscription.DoesNotExist:
            return False


# === ПУБЛИЧНЫЕ API ===
class PublicEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Event.objects.filter(organizer__slug=slug, is_active=True).order_by('date')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Event.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# === ПАНЕЛЬ УПРАВЛЕНИЯ ===
class DashboardEventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizer]
    
    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user.organizer).order_by('date')

    def perform_create(self, serializer):
        if not IsOrganizer.can_create_event(self.request.user):
            raise PermissionDenied('Лимит событий исчерпан. Оформите подписку Профи.')
        serializer.save(organizer=self.request.user.organizer)

    @action(detail=True, methods=['post'])
    def toggle_confirm(self, request, pk=None):
        event = self.get_object()
        event.is_confirmed = not event.is_confirmed
        event.save()
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'])
    def send_reminders(self, request, pk=None):
        event = self.get_object()
        sent_count = 0
        for lead in event.leads.all():
            if '@' in lead.contact:
                success = send_email_from_organizer(
                    organizer=event.organizer,
                    subject=f'Напоминание: {event.title}',
                    message=f'Привет, {lead.name}!\n\nЖдем вас завтра в {event.date.strftime("%H:%M")}.\nМесто: {event.location}',
                    recipient_list=[lead.contact]
                )
                if success:
                    sent_count += 1
        return Response({'status': 'ok', 'sent': sent_count})


class DashboardLeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        queryset = Lead.objects.filter(event__organizer=self.request.user.organizer).order_by('-created_at')
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        lead = self.get_object()
        event = lead.event
        
        if not event:
            return Response({'error': 'Лид не привязан к событию'}, status=400)
        if '@' not in lead.contact:
            return Response({'error': 'У лида нет Email'}, status=400)

        # ИСПОЛЬЗУЕМ НАСТРОЙКУ ВМЕСТО LOCALHOST
        invite_url = f"{settings.FRONTEND_URL}/invite/{lead.token}"
        
        success = send_email_from_organizer(
            organizer=event.organizer,
            subject=f"Приглашение на {event.title}",
            message=(
                f"Здравствуйте, {lead.name}!\n\n"
                f"Приглашаем вас на событие: {event.title}.\n"
                f"Дата: {event.date.strftime('%d.%m.%Y %H:%M')}\n"
                f"Место: {event.location}\n\n"
                f"Подтвердите участие: {invite_url}\n\n"
                f"С уважением,\n{event.organizer.name}"
            ),
            recipient_list=[lead.contact]
        )
        
        if success:
            lead.status = 'invited'
            lead.save()
            return Response({'status': 'ok', 'message': 'Приглашение отправлено'})
        else:
            return Response({'error': 'Ошибка отправки'}, status=500)


class PublicLeadCreateViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']


@api_view(['GET'])
@permission_classes([AllowAny])
def public_organizer_info(request, slug):
    organizer = get_object_or_404(Organizer, slug=slug)
    return Response({
        'name': organizer.name, 'slug': organizer.slug, 'bio': organizer.bio,
        'directions_data': organizer.directions_data,
        'guarantee_text': organizer.guarantee_text,
        'privacy_policy_url': organizer.privacy_policy_url,
        'offer_url': organizer.offer_url,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_organizer(request):
    data = request.data
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    slug = data.get('slug', '').strip().lower()
    bio = data.get('bio', '').strip()
    email = data.get('email', '').strip()

    if not username or not password or not name or not slug or not email:
        return Response({'error': 'Заполните все поля'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Пользователь уже существует'}, status=400)
    if Organizer.objects.filter(slug=slug).exists():
        return Response({'error': 'Slug занят'}, status=400)
    if not re.match(r'^[a-zа-яё0-9\-]+$', slug):
        return Response({'error': 'Ссылка может содержать только буквы (русские или английские), цифры и дефис'}, status=400)

    try:
        with transaction.atomic():
            settings_obj = SiteSettings.objects.first()
            require_verification = settings_obj.require_email_verification if settings_obj else True
            
            user = User.objects.create_user(
                username=username, 
                password=password, 
                email=email, 
                is_active=not require_verification
            )
            
            Organizer.objects.create(
                user=user,
                name=name,
                slug=slug,
                bio=bio,
                directions_data=[
                    {"id": "1", "title": "Мероприятия", "description": "Описание ваших мероприятий...", "icon": "01"}
                ],
                smtp_host='smtp.yandex.ru',
                smtp_port=465,
                smtp_use_ssl=True,
                smtp_user=email
            )
            
            free_plan = Plan.objects.filter(slug='free').first()
            if free_plan:
                Subscription.objects.create(user=user, plan=free_plan, is_active=True)
            
            if require_verification:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # ИСПОЛЬЗУЕМ НАСТРОЙКУ ВМЕСТО LOCALHOST
                verify_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
                
                send_mail(
                    subject="Подтвердите ваш Email",
                    message=f"Здравствуйте, {name}!\n\nПодтвердите аккаунт: {verify_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            
        if require_verification:
            return Response({
                'status': 'ok', 
                'message': 'Мы отправили письмо для подтверждения. Проверьте почту.',
                'requires_verification': True
            })
        else:
            return Response({
                'status': 'ok', 
                'message': 'Аккаунт успешно создан! Теперь вы можете войти.',
                'requires_verification': False
            })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    if not uidb64 or not token:
        return Response({'error': 'Неверная ссылка'}, status=400)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            return Response({'status': 'ok', 'message': 'Уже активирован'})
        user.is_active = True
        user.save()
        return Response({'status': 'ok', 'message': 'Аккаунт подтвержден!'})
    return Response({'error': 'Ссылка устарела'}, status=400)


class DashboardProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizer]
    
    def get_queryset(self):
        return Organizer.objects.filter(user=self.request.user)
        
    def list(self, request):
        org = request.user.organizer
        return Response({
            'name': org.name, 'bio': org.bio, 'slug': org.slug,
            'directions_data': org.directions_data,
            'yandex_email': org.yandex_email, 'yandex_app_password': org.yandex_app_password,
            'yandex_calendar_name': org.yandex_calendar_name,
            'guarantee_text': org.guarantee_text, 'privacy_policy_url': org.privacy_policy_url,
            'offer_url': org.offer_url,
            'smtp_host': org.smtp_host, 'smtp_port': org.smtp_port,
            'smtp_user': org.smtp_user, 'smtp_password': org.smtp_password,
            'smtp_use_ssl': org.smtp_use_ssl,
        })
        
    def create(self, request):
        org = request.user.organizer
        data = request.data
        org.name = data.get('name', org.name)
        org.bio = data.get('bio', org.bio)
        org.directions_data = data.get('directions_data', org.directions_data)
        org.yandex_email = data.get('yandex_email', org.yandex_email)
        org.yandex_app_password = data.get('yandex_app_password', org.yandex_app_password)
        org.guarantee_text = data.get('guarantee_text', org.guarantee_text)
        org.privacy_policy_url = data.get('privacy_policy_url', org.privacy_policy_url)
        org.offer_url = data.get('offer_url', org.offer_url)
        org.smtp_host = data.get('smtp_host', org.smtp_host)
        org.smtp_port = data.get('smtp_port', org.smtp_port)
        org.smtp_user = data.get('smtp_user', org.smtp_user)
        org.smtp_password = data.get('smtp_password', org.smtp_password)
        org.smtp_use_ssl = data.get('smtp_use_ssl', org.smtp_use_ssl)
        org.save()
        return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([IsOrganizer])
def upload_image(request):
    file = request.FILES.get('image')
    if not file:
        return Response({'error': 'Файл не найден'}, status=400)
    file_name = default_storage.save(f'directions/{file.name}', ContentFile(file.read()))
    return Response({'url': default_storage.url(file_name)})


@api_view(['POST'])
@permission_classes([IsOrganizer])
def invite_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id, event__organizer=request.user.organizer)
    event = lead.event
    if not event or '@' not in lead.contact:
        return Response({'error': 'Нет события или Email'}, status=400)
    
    # ИСПОЛЬЗУЕМ НАСТРОЙКУ ВМЕСТО LOCALHOST
    invite_url = f"{settings.FRONTEND_URL}/invite/{lead.token}"
    
    success = send_email_from_organizer(
        organizer=event.organizer,
        subject=f"Приглашение на {event.title}",
        message=f"Здравствуйте, {lead.name}!\n\nПриглашаем на {event.title}.\nДата: {event.date.strftime('%d.%m.%Y %H:%M')}\nМесто: {event.location}\n\nПодтвердите: {invite_url}",
        recipient_list=[lead.contact]
    )
    
    if success:
        lead.status = 'invited'
        lead.save()
        return Response({'status': 'ok'})
    return Response({'error': 'Ошибка'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_invite_info(request, token):
    lead = get_object_or_404(Lead, token=token)
    if not lead.event:
        return Response({'error': 'Событие не найдено'}, status=404)
    return Response({
        'lead_name': lead.name, 'event_title': lead.event.title,
        'event_date': lead.event.date.strftime('%d.%m.%Y %H:%M'),
        'event_location': lead.event.location, 'status': lead.status
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def respond_invite(request, token):
    lead = get_object_or_404(Lead, token=token)
    action = request.data.get('action')
    if action == 'accept':
        lead.status = 'accepted'
    elif action == 'decline':
        lead.status = 'declined'
    else:
        return Response({'error': 'Неверное действие'}, status=400)
    lead.save()
    return Response({'status': 'ok', 'message': 'Ваш ответ принят'})


@api_view(['GET'])
@permission_classes([IsOrganizer])
def get_all_contacts(request):
    contacts = Contact.objects.filter(organizer=request.user.organizer).order_by('-created_at')
    return Response([{'id': c.id, 'name': c.name, 'contact': c.contact} for c in contacts])


@api_view(['POST'])
@permission_classes([IsOrganizer])
def invite_contact_to_event(request):
    contact_id = request.data.get('contact_id')
    event_id = request.data.get('event_id')
    contact = get_object_or_404(Contact, id=contact_id, organizer=request.user.organizer)
    event = get_object_or_404(Event, id=event_id, organizer=request.user.organizer)
    
    if Lead.objects.filter(event=event, contact=contact.contact).exists():
        return Response({'error': 'Уже есть в списке'}, status=400)
        
    lead = Lead.objects.create(
        event=event, name=contact.name, contact=contact.contact,
        direction=event.direction, status='invited'
    )
    
    # ИСПОЛЬЗУЕМ НАСТРОЙКУ ВМЕСТО LOCALHOST
    invite_url = f"{settings.FRONTEND_URL}/invite/{lead.token}"
    send_email_from_organizer(
        organizer=event.organizer,
        subject=f"Приглашение на {event.title}",
        message=f"Здравствуйте, {contact.name}!\n\nПриглашаем на {event.title}.\nДата: {event.date.strftime('%d.%m.%Y %H:%M')}\nМесто: {event.location}\n\nПодтвердите: {invite_url}",
        recipient_list=[contact.contact]
    )
    
    return Response({'status': 'ok', 'message': 'Приглашение отправлено!'})


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email не указан'}, status=400)
    user = User.objects.filter(email=email, is_active=False).first()
    if not user:
        return Response({'error': 'Пользователь не найден'}, status=400)
    
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # ИСПОЛЬЗУЕМ НАСТРОЙКУ ВМЕСТО LOCALHOST
    verify_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
    
    send_mail(
        subject="Подтвердите Email (повторно)",
        message=f"Перейдите по ссылке: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False,
    )
    return Response({'status': 'ok', 'message': 'Письмо отправлено повторно'})


class PublicReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Review.objects.filter(organizer__slug=slug, is_approved=True).order_by('-created_at')

    def perform_create(self, serializer):
        slug = self.kwargs.get('slug')
        organizer = get_object_or_404(Organizer, slug=slug)
        serializer.save(organizer=organizer)


@api_view(['POST'])
@permission_classes([AllowAny])
def join_waitlist(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not event.is_full:
        return Response({'error': 'Есть свободные места'}, status=400)
    
    Lead.objects.create(
        event=event, name=request.data.get('name'),
        contact=request.data.get('contact'),
        direction=event.direction, is_waitlist=True
    )
    return Response({'status': 'ok', 'message': 'Вы в листе ожидания!'})


class DashboardReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return Review.objects.filter(organizer=self.request.user.organizer).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_approved = True
        review.save()
        return Response({'status': 'ok'})
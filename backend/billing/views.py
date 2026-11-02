from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Plan, Subscription
import yookassa
from yookassa import Payment
import uuid
from django.contrib.auth.models import User

# --- ВАШИ КЛЮЧИ ЮKASSA (положите в settings.py или .env) ---
# settings.YOOKASSA_SHOP_ID = 'ваш_shop_id'
# settings.YOOKASSA_SECRET_KEY = 'ваш_секретный_ключ'

@api_view(['GET'])
@permission_classes([AllowAny])
def get_plans(request):
    """Возвращает список всех тарифов"""
    plans = Plan.objects.all()
    data = [{
        'id': p.id, 'name': p.name, 'slug': p.slug, 'price': str(p.price),
        'max_events': p.max_events, 'has_calendar_sync': p.has_calendar_sync
    } for p in plans]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request, plan_id):
    """Создает платеж в ЮKassa и возвращает ссылку на оплату"""
    plan = get_object_or_404(Plan, id=plan_id)
    if plan.price == 0:
        return Response({'error': 'Этот тариф бесплатный'}, status=400)

    user = request.user
    
    # Настраиваем ЮKassa
    yookassa.Configuration.account_id = settings.YOOKASSA_SHOP_ID
    yookassa.Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    # Создаем платеж
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": str(plan.price),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{settings.FRONTEND_URL}/dashboard?payment_success=true"
        },
        "capture": True,
        "description": f"Подписка на тариф {plan.name} ({user.email})",
        "metadata": {
            "user_id": user.id,
            "plan_id": plan.id
        }
    }, idempotence_key)

    # Сохраняем ID платежа в подписке пользователя (пока не активна)
    sub, _ = Subscription.objects.get_or_create(user=user)
    sub.payment_id = payment.id
    sub.plan = plan # Временно запоминаем план
    sub.save()

    return Response({
        'payment_url': payment.confirmation.confirmation_url,
        'payment_id': payment.id
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def yookassa_webhook(request):
    """Вебхук для приема уведомлений от ЮKassa"""
    event = request.data.get('event')
    
    if event == 'payment.succeeded':
        payment_data = request.data.get('object')
        metadata = payment_data.get('metadata', {})
        user_id = metadata.get('user_id')
        plan_id = metadata.get('plan_id')
        
        if user_id and plan_id:
            try:
                user = User.objects.get(id=user_id)
                plan = Plan.objects.get(id=plan_id)
                sub, _ = Subscription.objects.get_or_create(user=user)
                
                # Активируем подписку на 30 дней
                sub.plan = plan
                sub.extend(30)
                sub.save()
                
                print(f"✅ Подписка для {user.username} активирована до {sub.expires_at}")
            except Exception as e:
                print(f"Ошибка активации подписки: {e}")

    return Response({'status': 'ok'})
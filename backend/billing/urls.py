from django.urls import path
from .views import get_plans, create_payment, yookassa_webhook

urlpatterns = [
    path('plans/', get_plans, name='get_plans'),
    path('pay/<int:plan_id>/', create_payment, name='create_payment'),
    path('webhook/yookassa/', yookassa_webhook, name='yookassa_webhook'),
]
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from leads.views import (
    DashboardProfileViewSet,
    PublicEventViewSet, 
    DashboardEventViewSet, 
    DashboardLeadViewSet, 
    PublicLeadCreateViewSet,
    get_all_contacts,
    get_invite_info,
    invite_contact_to_event,
    invite_lead, 
    public_organizer_info,
    register_organizer,
    resend_verification,
    respond_invite,
    upload_image,
    verify_email,
)

router = DefaultRouter()
router.register(r'dashboard/events', DashboardEventViewSet, basename='dashboard-events')
router.register(r'dashboard/leads', DashboardLeadViewSet, basename='dashboard-leads')
router.register(r'leads', PublicLeadCreateViewSet, basename='leads')
router.register(r'dashboard/profile', DashboardProfileViewSet, basename='dashboard-profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Публичные эндпоинты
    path('api/public/<slug:slug>/info/', public_organizer_info, name='public-organizer-info'),
    path('api/public/<slug:slug>/events/', PublicEventViewSet.as_view({'get': 'list'}), name='public-events'),
    path('api/leads/<int:lead_id>/invite/', invite_lead, name='invite_lead'),
    path('api/invite/<uuid:token>/', get_invite_info, name='get_invite_info'),
    path('api/invite/<uuid:token>/respond/', respond_invite, name='respond_invite'),
    path('api/contacts/', get_all_contacts, name='get_all_contacts'),
    path('api/invite-contact/', invite_contact_to_event, name='invite_contact_to_event'),
    path('api/verify-email/', verify_email, name='verify_email'),
    path('api/resend-verification/', resend_verification, name='resend_verification'),
    
    # Авторизация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/register/', register_organizer, name='register'),
    
    # ЗАГРУЗКА ФОТО
    path('api/upload/', upload_image, name='upload_image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from rest_framework import serializers
from .models import Event, Lead, Organizer

class EventSerializer(serializers.ModelSerializer):
    lead_count = serializers.ReadOnlyField()
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('organizer', 'yandex_uid', 'is_confirmed', 'reminders_sent')

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
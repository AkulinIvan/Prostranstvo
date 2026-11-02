from rest_framework import serializers
from .models import Event, Lead, Organizer, Review

class EventSerializer(serializers.ModelSerializer):
    lead_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('organizer', 'yandex_uid', 'is_confirmed', 'reminders_sent', 'view_count')

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author_name', 'text', 'rating', 'created_at']
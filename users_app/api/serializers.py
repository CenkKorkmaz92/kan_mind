from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        full = obj.first_name
        if obj.last_name:
            full = f"{obj.first_name} {obj.last_name}"
        return full.strip()

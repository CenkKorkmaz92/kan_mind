from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('fullname', 'email', 'password', 'repeated_password')

    def validate(self, data):
        """
        Validate that the passwords match and the email does not already exist.
        Raises ValidationError if validation fails.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'email': 'Email already exists.'})
        return data

    def create(self, validated_data):
        """
        Create a new user with the provided validated data and generate an auth token.
        """
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['fullname']
        )
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

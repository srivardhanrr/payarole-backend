from rest_framework import serializers
from .models import User

class PhoneNumberSerializer(serializers.Serializer):
   phone_number = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
   phone_number = serializers.CharField()
   otp = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
   class Meta:
       model = User
       fields = ('id', 'phone_number', 'full_name', 'email')
       read_only_fields = ('id', 'phone_number')

class TokenResponseSerializer(serializers.Serializer):
   token = serializers.CharField()
   is_profile_complete = serializers.BooleanField()
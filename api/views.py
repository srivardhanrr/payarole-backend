from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.utils import timezone
import random

from .authentication import JWTAuthentication
from .serializers import (
    PhoneNumberSerializer,
    OTPVerifySerializer,
    UserProfileSerializer,
    TokenResponseSerializer
)
from .models import User
from .utils.auth import generate_token
from .utils.sms_service import send_sms


class RequestOTPView(APIView):
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone_number']
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        cache.set(f'otp:{phone}', otp, timeout=600)  # 10 minutes

        send_sms(phone, otp)
        print(f"OTP for {phone}: {otp}")

        return Response({'message': 'OTP sent successfully'})


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']

        stored_otp = cache.get(f'otp:{phone}')
        if not stored_otp or stored_otp != otp:
            return Response(
                {'error': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(phone_number=phone).first()
        is_new_user = user is None

        if is_new_user:
            user = User.objects.create(phone_number=phone)

        user.last_login = timezone.now()
        user.save()

        cache.delete(f'otp:{phone}')
        token = generate_token(user)
        print(token)

        response_serializer = TokenResponseSerializer(data={
            'token': token,
            'is_profile_complete': not is_new_user
        })
        response_serializer.is_valid()
        return Response(response_serializer.data)


class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(serializer.data)


class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
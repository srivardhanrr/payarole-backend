from django.urls import path
from .views import (
   RequestOTPView,
   VerifyOTPView,
   CompleteProfileView,
   UserProfileView, RandomUser
)

app_name = 'authentication'

urlpatterns = [
   path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
   path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
   path('complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
   path('profile/', UserProfileView.as_view(), name='profile'),
   path('random-user/', RandomUser.as_view(), name='random-user'),
]
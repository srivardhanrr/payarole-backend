# auth.py
from datetime import datetime, timedelta
from jwt import encode, decode
from django.conf import settings

def generate_token(user):
    payload = {
        'user_id': str(user.id),
        'phone_number': user.phone_number,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return encode(payload, settings.SECRET_KEY, algorithm='HS256')

# Add to settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'path.to.your.JWTAuthentication',
    ],
}


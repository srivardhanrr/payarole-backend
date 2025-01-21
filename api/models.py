import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.base_user import AbstractBaseUser


phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
        ]
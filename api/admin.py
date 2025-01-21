from django.contrib import admin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
   list_display = ('id', 'phone_number', 'full_name', 'email', 'is_active', 'last_login', 'created_at')
   list_filter = ('is_active', 'created_at')
   search_fields = ('phone_number', 'full_name', 'email')
   readonly_fields = ('id', 'last_login', 'created_at', 'updated_at')
   ordering = ('-created_at',)

   def get_readonly_fields(self, request, obj=None):
       if obj:
           return self.readonly_fields + ('phone_number',)
       return self.readonly_fields

   def has_delete_permission(self, request, obj=None):
       return False
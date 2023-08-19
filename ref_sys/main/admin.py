from django.contrib import admin
from .models import UserProfile, InvitationUsage, AuthorizationCode

admin.site.register(UserProfile)

admin.site.register(InvitationUsage)
admin.site.register(AuthorizationCode)
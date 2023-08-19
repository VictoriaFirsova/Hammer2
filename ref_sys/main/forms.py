from django import forms
from .models import UserProfile, InvitationUsage, AuthorizationCode


class UserForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']


class InvitationUsageForm(forms.ModelForm):
    class Meta:
        model = InvitationUsage
        fields = ['invitee_phone', 'used_invite_code']


class AuthorizationCodeForm(forms.ModelForm):
    class Meta:
        model = AuthorizationCode
        fields = ['phone', 'code']
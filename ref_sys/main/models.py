from django.db import models


class UserProfile(models.Model):
    phone = models.CharField(max_length=11, unique=True, primary_key=True)
    invite_code = models.CharField(max_length=6, blank=True, null=True, unique=True)
    used_invite_codes = models.ManyToManyField('self', related_name='used_by', blank=True)
    has_entered_invite_code = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return self.phone


class InvitationUsage(models.Model):
    inviter_phone = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='inviter_phone')
    used_invite_code = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='used_invite_code')
    invitee_phone = models.CharField(max_length=11)
    objects = models.Manager()


class AuthorizationCode(models.Model):
    phone = models.CharField(max_length=11)
    code = models.CharField(max_length=4)
    is_used = models.BooleanField(default=False)
    objects = models.Manager()
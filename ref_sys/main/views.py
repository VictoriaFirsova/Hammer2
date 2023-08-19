from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, DjangoModelPermissionsOrAnonReadOnly

from .models import UserProfile, InvitationUsage, AuthorizationCode
from .forms import UserForm, InvitationUsageForm, AuthorizationCodeForm
import random
import string
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileCreateSerializer, AuthorizationCodeSerializer, \
    UserProfileInviteCodeSerializer, AuthorizationCodeVerifySerializer


def index(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        phone = request.POST['phone']
        try:
            if form.is_valid():
                user_profile = UserProfile.objects.create(phone=phone)
                invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                user_profile.invite_code = invite_code

                user_profile.save()
        except IntegrityError:
            existing_code = AuthorizationCode.objects.get(phone=phone).code
            auth_url = reverse('authentication') + f'?phone={phone}&code={existing_code}'
            return redirect(auth_url)

            # Генерация случайного кода
        code = ''.join(random.choices(string.digits, k=4))
        auth_code = AuthorizationCode.objects.create(phone=phone, code=code)

        auth_url = reverse('authentication') + f'?phone={phone}&code={code}'
        return redirect(auth_url)
    else:
        form = UserForm()

    context = {'form': form}
    return render(request, 'index.html', context)


def authentication(request):
    phone = request.GET.get('phone')
    code = request.GET.get('code')

    if request.method == 'POST':
        entered_code = request.POST.get('code_input')

        if entered_code == code:
            auth_code = AuthorizationCode.objects.get(phone=phone, code=code, is_used=False)
            auth_code.is_used = True
            auth_code.save()
            profile_url = reverse('profile') + f'?phone={phone}&code={code}'
            return redirect(profile_url)

    context = {'phone': phone, 'code': code}
    return render(request, 'authentication.html', context)


def profile(request):
    user_profile = None
    error_message = None
    user_invite_code = None
    user_phone = None

    if request.method == 'GET':
        phone = request.GET.get('phone', None)
        code = request.GET.get('code', None)
        if phone and code:
            try:
                user_profile = UserProfile.objects.get(phone=phone)
            except UserProfile.DoesNotExist:
                pass

    elif request.method == 'POST':
        user_phone = request.POST.get('user_phone')
        user_invite_code = request.POST.get('user_invite_code')
        entered_code = request.POST.get('entered_code')

        if user_phone and user_invite_code and entered_code:
            try:
                inviter_user_profile = UserProfile.objects.get(phone=user_phone, invite_code=user_invite_code)
                invitee_user_profile = UserProfile.objects.get(invite_code=entered_code)

                if inviter_user_profile.invite_code != entered_code and not invitee_user_profile.has_entered_invite_code:
                    invitee_user_profile.has_entered_invite_code = True
                    invitee_user_profile.used_invite_codes.add(inviter_user_profile)
                elif invitee_user_profile.has_entered_invite_code:
                    error_message = 'Вы уже вводили инвайт-код, больше этого сделать нельзя'
                else:
                    error_message = 'Недействительный инвайт-код'

            except UserProfile.DoesNotExist:
                error_message = 'Пользователь с таким номером и инвайт-кодом не найден'

    used_invitations = user_profile.used_invite_codes.all() if user_profile else []

    context = {'user_profile': user_profile, 'used_invitations': used_invitations, 'error_message': error_message}
    if request.method == 'POST':
        return redirect(f'/profile/?phone={user_phone}&code={user_invite_code}')
    return render(request, 'profile.html', context)


def used_invite_codes_api(request, phone):
    try:
        user_profile = UserProfile.objects.get(phone=phone)

        if user_profile.used_invite_codes.exists():
            used_invite_phones = [invite.phone for invite in user_profile.used_invite_codes.all()]

            response_data = {
                'used_invite_phones': used_invite_phones
            }
        else:
            response_data = {
                'message': 'No used invite codes for this user'
            }

        return JsonResponse(response_data)
    except UserProfile.DoesNotExist:
        response_data = {
            'error': 'User profile not found'
        }

        return JsonResponse(response_data, status=404)


class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        # Вернуть нужную выборку данных, например:
        return UserProfile.objects.filter(phone=self.request.user.phone)


class UserProfileDetail(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()  # Указываем queryset для доступа к данным
    serializer_class = UserProfileSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    lookup_field = 'phone'  # Указываем поле, по которому будет производиться поиск

    def get_queryset(self):
        return UserProfile.objects.all()


class UserProfileCreate(APIView):
    permission_classes = [AllowAny]  # Разрешить доступ для всех

    def post(self, request, phone):
        try:
            user_profile = UserProfile.objects.get(phone=phone)
            auth_code = ''.join(random.choices(string.digits, k=4))
            try:
                auth_code_entry = AuthorizationCode.objects.get(phone=phone)
                auth_code_entry.code = auth_code
                auth_code_entry.save()
            except AuthorizationCode.DoesNotExist:
                AuthorizationCode.objects.create(phone=phone, code=auth_code)
            return Response({'message': f'Пользователь уже существует. Код авторизации обновлен: {auth_code}'})
        except UserProfile.DoesNotExist:
            # Создаем профиль пользователя и генерируем код авторизации
            user_profile = UserProfile.objects.create(phone=phone)
            auth_code = ''.join(random.choices(string.digits, k=4))
            AuthorizationCode.objects.create(phone=phone, code=auth_code)

            return Response({'message': f'Пользователь создан. Код авторизации {auth_code}.'})


class AuthorizationView(APIView):
    def get(self, request, phone, code):
        try:
            auth_code = AuthorizationCode.objects.get(phone=phone, code=code)
        except AuthorizationCode.DoesNotExist:
            return Response({"detail": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_profile = UserProfile.objects.get(phone=phone)
            if user_profile.invite_code:
                invite_code = user_profile.invite_code
            else:
                # Генерируем инвайт-код для пользователя, у которого нет кода
                invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                user_profile.invite_code = invite_code
                user_profile.save()
        except UserProfile.DoesNotExist:
            # Генерируем инвайт-код для нового пользователя
            invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            UserProfile.objects.create(phone=phone, invite_code=invite_code)

        return Response({"detail": f"Код подтвержден и инвайт-код создан: {invite_code}"}, status=status.HTTP_200_OK)


class UserProfileGenerateInviteCode(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileCreateSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        instance.invite_code = invite_code
        instance.save()


class UserProfileEnterOtherInviteCode(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileInviteCodeSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        entered_invite_code = request.data.get('entered_invite_code')

        if not entered_invite_code:
            return Response({"detail": "Введите инвайт-код"}, status=status.HTTP_400_BAD_REQUEST)
        if instance.has_entered_invite_code:
            return Response({"detail": "Вы уже добавили инвайт-код"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            inviter_user_profile = UserProfile.objects.get(invite_code=entered_invite_code)
            if inviter_user_profile == instance:
                return Response({"detail": "Вы не можете использовать свой собственный инвайт-код"},
                                status=status.HTTP_400_BAD_REQUEST)

            instance.used_invite_codes.add(inviter_user_profile)
            instance.has_entered_invite_code = True
            instance.save()
            return Response({"detail": "Инвайт-код успешно добавлен"}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Недействительный инвайт-код"}, status=status.HTTP_400_BAD_REQUEST)
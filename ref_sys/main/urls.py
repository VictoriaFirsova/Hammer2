from django.urls import path
from . import views
from .views import UserProfileCreate, AuthorizationView, UserProfileGenerateInviteCode, \
    UserProfileEnterOtherInviteCode

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('', views.index, name='index'),
    path('authentication/', views.authentication, name='authentication'),
    path('api/profiles/<str:phone>/used_invite_codes/', views.used_invite_codes_api, name='used_invite_codes_api'),
    path('api/profiles/', views.UserProfileList.as_view(), name='userprofile-list'),
    path('api/profiles/<str:phone>/', views.UserProfileDetail.as_view(), name='userprofile-detail'),

    path('api/profiles/create/<str:phone>/', UserProfileCreate.as_view(), name='create-profile'),
    path('api/authorization/<str:phone>/<str:code>/', AuthorizationView.as_view(), name='verify-authorization'),
    path('api/profiles/<str:phone>/generate_invite_code/', UserProfileGenerateInviteCode.as_view(), name='generate-invite-code'),
    path('api/profiles/<str:pk>/enter_invite_code/', UserProfileEnterOtherInviteCode.as_view(), name='enter-invite-code'),
]

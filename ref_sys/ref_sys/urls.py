from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ref_sys.main.views import UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('api/', include(router.urls)),
]

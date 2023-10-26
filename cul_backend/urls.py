from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from api.views import Logout, SuperUserView, sessionlogout


urlpatterns = [
    path("admin/", admin.site.urls),

    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.authtoken')), 
    path('api/v1/accounts/',include('accounts.urls')),
    path('api/v1/',include('api.urls')),
    path('api/v1/person/logout/',Logout.as_view()),
    path('api/v1/general/',include('app_general.urls')),
    path('superuser/', SuperUserView.as_view(), name="dashboard"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from . import views

from django.urls import path


urlpatterns = [
    path('getColleges',views.GetColleges.as_view()),
]

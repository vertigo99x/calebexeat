from django.urls import path

from . import views

urlpatterns = [
   path('',views.AllUsersView.as_view()),
   path('student/<str:matric_no>/',views.GetStudentData.as_view()),
   path('userdata/',views.GetUserData.as_view()),
   path('users/password/change/',views.ChangePassword.as_view()),
   
]

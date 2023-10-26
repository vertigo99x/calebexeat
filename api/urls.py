from django.urls import path

from . import views

urlpatterns = [
   path('forms',views.FormView.as_view()),
   path('forms/task',views.ApproveOrRejectForm.as_view()),
   path('forms/search',views.SearchForms.as_view()),
   path('forms/cancel',views.CancelForm.as_view()),
   path('events',views.EventView.as_view()),
   path('limiter_check',views.FirstLoginView.as_view()),
   
]

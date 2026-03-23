from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login_view),
    path('google/', views.google_login),
    path('profile/', views.get_profile),
    path('token/refresh/', TokenRefreshView.as_view()),
]
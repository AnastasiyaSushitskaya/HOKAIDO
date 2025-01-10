from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('main/', views.index, name='index'),  # Главная страница
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

]
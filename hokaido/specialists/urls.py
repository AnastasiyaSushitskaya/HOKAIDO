from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('main/', views.index, name='index'),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('menu/', views.menu_view, name='menu'),
    path('mini_games/', views.mini_games_view, name='mini_games'),
    path('specialists/', views.specialists_view, name='specialists'),
    path('clue/', views.clue_view, name='clue'),
    path('personal/', views.personal_view, name='personal'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

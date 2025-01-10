from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view),
    path('exel/<int:file_id>/', views.edit_excel, name='edit_excel'),  # URL с передачей file_id

]
from django.urls import path
from . import views

app_name = 'users'  # <- esto es clave para usar namespace

urlpatterns = [
    path('', views.user_list, name='user_list'),  # ejemplo de vista
]

from django.urls import path
from .views import home_view, about_us_view, register_view, contact_view
from django.contrib.auth import views as auth_views

app_name = 'core'  # Namespace para poder usar {% url 'core:home' %}

urlpatterns = [
    path("", home_view, name='home'),
    path("sobre-nosotros/", about_us_view, name='about_us'),
    path('registro/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html',next_page='core:home'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    path("contacta-con-nosotros/", contact_view, name='contact'),
]

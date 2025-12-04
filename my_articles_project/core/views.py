from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .utils import send_notification_email



# Vista de home
def home_view(request):
    return render(request, "core/home.html")

# Vista sobre nosotros
def about_us_view(request):
    return render(request, "core/about_us.html")

# Vista de contacto
def contact_view(request):
    return render(request, "core/contact.html")

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Enviar email
            send_notification_email(
                subject="Bienvenido a My Articles!",
                message=f"Hola {user.username}, gracias por registrarte.",
                recipient_list=[user.email]
            )
            return redirect('core:home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})
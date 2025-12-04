from django.shortcuts import render

def user_list(request):
    return render(request, "users/user_list.html")

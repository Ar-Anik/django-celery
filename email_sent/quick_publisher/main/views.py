from django.shortcuts import render, redirect
from django.http import Http404
from .models import MyUser

# Create your views here.

def home(request):
    return render(request, 'home.html')

def verify(request, uuid):
    try:
        user = MyUser.objects.get(verification_uuid=uuid, is_verified=False)
    except MyUser.DoesNotExist:
        return render(request, 'message.html')

    user.is_verified = True
    user.save()

    return redirect('home')

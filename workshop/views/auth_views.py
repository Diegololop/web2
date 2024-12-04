from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from ..forms.auth_forms import ClientRegistrationForm, LoginForm, ClientActivationForm
from ..models import Reservation, Product, Client
from django.utils import timezone
from datetime import datetime

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Has iniciado sesión exitosamente.')
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'workshop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada exitosamente.')
            return redirect('dashboard')
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'workshop/register.html', {'form': form})

def activate_account(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ClientActivationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta activada exitosamente.')
            return redirect('dashboard')
    else:
        form = ClientActivationForm()

    return render(request, 'workshop/client_activation.html', {'form': form})
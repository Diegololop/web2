from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Product, WorkOrder, Client, Reservation

def home(request):
    services = Product.objects.filter(category='service')
    context = {
        'services': services,
    }
    return render(request, 'workshop/home.html', context)

def service_list_public(request):
    services = Product.objects.filter(category='service')
    context = {
        'services': services,
    }
    return render(request, 'workshop/service_list_public.html', context)

def product_list_public(request):
    products = Product.objects.filter(category='product')
    context = {
        'products': products,
    }
    return render(request, 'workshop/product_list_public.html', context)

def vehicle_tracking(request):
    work_orders = []
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(user=request.user)
            work_orders = WorkOrder.objects.filter(client=client)
        except Client.DoesNotExist:
            pass
    
    context = {
        'work_orders': work_orders,
    }
    return render(request, 'workshop/vehicle_tracking.html', context)

@login_required
def dashboard(request):
    user_profile = request.user.userprofile if hasattr(request.user, 'userprofile') else None
    context = {
        'user_profile': user_profile,
    }
    
    if request.user.is_superuser or (user_profile and user_profile.role == 'admin'):
        context.update({
            'clients': Client.objects.all()[:5],
            'services': Product.objects.filter(category='service'),
            'work_orders': WorkOrder.objects.all()[:5],
            'reservations': Reservation.objects.filter(status='pending'),
        })
    elif user_profile and user_profile.role == 'mechanic':
        context['work_orders'] = WorkOrder.objects.filter(mechanic=user_profile)
    elif user_profile and user_profile.role == 'receptionist':
        context.update({
            'clients': Client.objects.all()[:5],
            'work_orders': WorkOrder.objects.all()[:5],
            'reservations': Reservation.objects.all(),
        })
    else:
        try:
            client = Client.objects.get(user=request.user)
            context.update({
                'work_orders': WorkOrder.objects.filter(client=client),
                'reservations': Reservation.objects.filter(client=client),
            })
        except Client.DoesNotExist:
            pass
    
    return render(request, 'workshop/dashboard.html', context)
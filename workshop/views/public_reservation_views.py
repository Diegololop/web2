from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from ..models import Client, Product, Reservation

def reservation_form(request):
    if request.method == 'POST':
        if 'add_to_cart' in request.POST:
            service_id = request.POST.get('service')
            if service_id:
                service = get_object_or_404(Product, id=service_id, category='service')
                cart_services = request.session.get('cart_services', [])
                if service_id not in cart_services:
                    cart_services.append(service_id)
                    request.session['cart_services'] = cart_services
                    messages.success(request, f'Servicio "{service.name}" agregado.')
                else:
                    messages.warning(request, 'Este servicio ya está en el carrito.')
            return redirect('reservation_form')
        
        elif 'remove_from_cart' in request.POST:
            service_id = request.POST.get('service_id')
            cart_services = request.session.get('cart_services', [])
            if service_id in cart_services:
                cart_services.remove(service_id)
                request.session['cart_services'] = cart_services
                messages.success(request, 'Servicio eliminado del carrito.')
            return redirect('reservation_form')
        
        elif 'reservation_form' in request.POST:
            try:
                cart_services = request.session.get('cart_services', [])
                if not cart_services:
                    messages.error(request, 'Debe seleccionar al menos un servicio.')
                    return redirect('reservation_form')
                
                services = Product.objects.filter(id__in=cart_services)
                date = request.POST.get('date')
                time = request.POST.get('time')
                service_date = timezone.make_aware(
                    datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                )
                
                if request.user.is_authenticated:
                    client = Client.objects.get(user=request.user)
                else:
                    client = Client.objects.create(
                        user=User.objects.create_user(
                            username=request.POST.get('email'),
                            email=request.POST.get('email'),
                            first_name=request.POST.get('first_name'),
                            last_name=request.POST.get('last_name')
                        ),
                        phone=request.POST.get('phone'),
                        address='Temporal'
                    )
                
                total_duration = sum(service.duration or 0 for service in services)
                total_price = sum(service.price for service in services)
                
                reservation = Reservation.objects.create(
                    client=client,
                    service_date=service_date,
                    description=request.POST.get('description', ''),
                    total_duration=total_duration,
                    total_price=total_price,
                    status='pending'
                )
                reservation.services.set(services)
                
                del request.session['cart_services']
                
                messages.success(request, 'Reserva creada exitosamente.')
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error al crear la reserva: {str(e)}')
                return redirect('reservation_form')
    
    cart_services = Product.objects.filter(id__in=request.session.get('cart_services', []))
    total_duration = sum(service.duration or 0 for service in cart_services)
    total_price = sum(service.price for service in cart_services)
    
    return render(request, 'workshop/reservation_form.html', {
        'services': Product.objects.filter(category='service'),
        'cart_services': cart_services,
        'total_duration': total_duration,
        'total_price': total_price
    })

def check_availability(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Fecha requerida'}, status=400)

    try:
        check_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        if check_date < timezone.now().date():
            return JsonResponse({
                'all_hours': [], 
                'message': 'No se pueden hacer reservas en fechas pasadas'
            })

        if check_date.weekday() >= 5:
            return JsonResponse({
                'all_hours': [], 
                'message': 'No hay atención los fines de semana'
            })
        
        work_hours = []
        start_time = datetime.strptime('09:00', '%H:%M').time()
        end_time = datetime.strptime('17:30', '%H:%M').time()
        
        current_time = start_time
        while current_time <= end_time:
            slot_datetime = timezone.make_aware(datetime.combine(check_date, current_time))
            
            if check_date == timezone.now().date() and current_time <= timezone.now().time():
                current_time = (datetime.combine(check_date, current_time) + 
                              timedelta(minutes=30)).time()
                continue

            existing_reservations = Reservation.objects.filter(
                service_date=slot_datetime,
                status__in=['pending', 'confirmed']
            ).count()
            
            work_hours.append({
                'time': current_time.strftime('%H:%M'),
                'available': existing_reservations == 0,
                'reason': 'Horario ocupado' if existing_reservations > 0 else None
            })
            
            current_time = (datetime.combine(check_date, current_time) + 
                          timedelta(minutes=30)).time()
        
        return JsonResponse({
            'all_hours': work_hours,
            'message': None if work_hours else 'No hay horarios disponibles para esta fecha'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
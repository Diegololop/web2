from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.models import User
from ..models import Product, Reservation, Client, BusinessHours
from ..forms.reservation_forms import ReservationModelForm
from ..decorators import receptionist_required

def reservation_form(request, reservation_id=None):
    """Vista unificada para crear/editar reservas"""
    # Verificar si es una edición
    if reservation_id:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'userprofile') and request.user.userprofile.role in ['admin', 'receptionist'])):
            messages.error(request, 'No tiene permisos para editar reservas.')
            return redirect('dashboard')
        action = 'Editar'
    else:
        reservation = None
        action = 'Crear'

    if request.method == 'POST':
        # Procesar el formulario según el tipo de usuario
        if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.role in ['admin', 'receptionist']:
            # Administrador/Recepcionista
            form = ReservationModelForm(request.POST, instance=reservation)
            if form.is_valid():
                form.save()
                messages.success(request, f'Reserva {action.lower()}da exitosamente.')
                return redirect('reservation_list')
        else:
            # Cliente o usuario no registrado
            try:
                # Obtener servicios seleccionados
                service_ids = request.POST.getlist('services')
                services = Product.objects.filter(id__in=service_ids)
                
                if not services:
                    messages.error(request, 'Debe seleccionar al menos un servicio.')
                    return redirect('reservation_form')

                # Calcular totales
                total_duration = sum(service.duration or 0 for service in services)
                total_price = sum(service.price for service in services)

                # Obtener o crear cliente
                if request.user.is_authenticated and hasattr(request.user, 'client'):
                    client = request.user.client
                else:
                    # Crear usuario y cliente para visitante
                    first_name = request.POST.get('first_name')
                    last_name = request.POST.get('last_name')
                    email = request.POST.get('email')
                    phone = request.POST.get('phone')
                    rut = request.POST.get('rut')

                    if not all([first_name, last_name, email, phone, rut]):
                        messages.error(request, 'Todos los campos son requeridos.')
                        return redirect('reservation_form')

                    # Crear usuario
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=User.objects.make_random_password()
                    )

                    # Crear cliente
                    client = Client.objects.create(
                        user=user,
                        rut=rut,
                        phone=phone,
                        address="Pendiente"
                    )

                # Crear reserva
                date = request.POST.get('date')
                time = request.POST.get('time')
                if not date or not time:
                    messages.error(request, 'Debe seleccionar fecha y hora.')
                    return redirect('reservation_form')

                service_date = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                service_date = timezone.make_aware(service_date)

                reservation = Reservation.objects.create(
                    client=client,
                    service_date=service_date,
                    description=request.POST.get('description', ''),
                    total_duration=total_duration,
                    total_price=total_price,
                    status='pending'
                )
                reservation.services.set(services)

                messages.success(request, 'Reserva creada exitosamente.')
                if not request.user.is_authenticated:
                    messages.info(request, 'Para ver su reserva, active su cuenta con el email y RUT proporcionados.')
                    return redirect('activate_account')
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f'Error al crear la reserva: {str(e)}')
                return redirect('reservation_form')
    else:
        # Mostrar formulario según el tipo de usuario
        if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.role in ['admin', 'receptionist']:
            form = ReservationModelForm(instance=reservation)
        else:
            form = None

    services = Product.objects.filter(category='service')
    return render(request, 'workshop/reservation_form.html', {
        'form': form,
        'services': services,
        'action': action,
        'reservation': reservation
    })

@login_required
@receptionist_required
def reservation_list(request):
    """Vista de lista de reservas"""
    search_date = request.GET.get('date')
    reservations = Reservation.objects.all().order_by('-service_date')
    
    if search_date:
        try:
            date = datetime.strptime(search_date, '%Y-%m-%d').date()
            reservations = reservations.filter(service_date__date=date)
        except ValueError:
            messages.error(request, 'Formato de fecha inválido')
    
    return render(request, 'workshop/admin/reservation_list.html', {
        'reservations': reservations,
        'search_date': search_date
    })

@login_required
@receptionist_required
def reservation_delete(request, reservation_id):
    """Vista para eliminar/cancelar reservas"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Reserva cancelada exitosamente.')
        return redirect('reservation_list')
    
    return render(request, 'workshop/admin/reservation_confirm_delete.html', {
        'reservation': reservation
    })

def get_time_slots(request):
    """API para obtener horarios disponibles"""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Fecha requerida'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        business_hours = BusinessHours.objects.get(day=date.weekday())
        
        if business_hours.is_closed:
            return JsonResponse({'slots': [], 'message': 'Cerrado este día'})
        
        # Generar slots cada 30 minutos
        slots = []
        current_time = datetime.combine(date, business_hours.open_time)
        end_time = datetime.combine(date, business_hours.close_time)
        
        while current_time < end_time:
            slot_time = current_time.strftime('%H:%M')
            # Verificar disponibilidad
            is_available = not Reservation.objects.filter(
                service_date__date=date,
                service_date__hour=current_time.hour,
                service_date__minute=current_time.minute
            ).exists()
            
            slots.append({
                'time': slot_time,
                'available': is_available,
                'reason': 'Horario ocupado' if not is_available else None
            })
            current_time += timedelta(minutes=30)
        
        return JsonResponse({'slots': slots})
    except (ValueError, BusinessHours.DoesNotExist):
        return JsonResponse({'error': 'Error al obtener horarios'}, status=400)
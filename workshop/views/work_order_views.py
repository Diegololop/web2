from datetime import datetime, timedelta
from urllib import request
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ..models import WorkOrder, WorkOrderNote, Client, UserProfile
from ..forms.work_order_forms import WorkOrderForm, WorkOrderNoteForm
from ..decorators import receptionist_required, mechanic_required

@login_required
@receptionist_required
def work_order_list(request):
    """Lista de órdenes de trabajo"""
    work_orders = WorkOrder.objects.all().order_by('-created_at')
    return render(request, 'workshop/admin/work_order_list.html', {
        'work_orders': work_orders
    })

@login_required
@receptionist_required
def work_order_add(request):
    """Crear nueva orden de trabajo"""
    if request.method == 'POST':
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.created_at = timezone.now()
            work_order.save()
            
            # Crear nota inicial si hay descripción
            if work_order.description:
                WorkOrderNote.objects.create(
                    work_order=work_order,
                    user=request.user,
                    note=f"Orden de trabajo creada: {work_order.description}"
                )
            
            messages.success(request, 'Orden de trabajo creada exitosamente.')
            return redirect('work_order_list')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = WorkOrderForm()
    
    context = {
        'form': form,
        'action': 'Crear'
    }
    return render(request, 'workshop/admin/work_order_form.html', context)

@login_required
def work_order_edit(request, order_id):
    """Editar orden de trabajo existente"""
    work_order = get_object_or_404(WorkOrder, id=order_id)
    
    # Verificar permisos
    if not (request.user.is_superuser or 
            hasattr(request.user, 'userprofile') and 
            request.user.userprofile.role in ['admin', 'mechanic', 'receptionist']):
        messages.error(request, 'No tiene permisos para editar órdenes de trabajo.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Manejar cambio de estado
        if 'change_status' in request.POST:
            new_status = request.POST.get('change_status')
            note_text = request.POST.get('note', '')
            
            if new_status == 'cancelled' and not note_text:
                messages.error(request, 'Debe proporcionar un motivo para cancelar la orden.')
                return redirect('work_order_edit', order_id=order_id)
            
            work_order.status = new_status
            work_order.save()
            
            # Crear nota sobre el cambio de estado
            WorkOrderNote.objects.create(
                work_order=work_order,
                user=request.user,
                note=f"Estado cambiado a: {work_order.get_status_display()}" + 
                     (f"\nMotivo: {note_text}" if note_text else ""),
                is_cancel_reason=new_status == 'cancelled'
            )
            
            messages.success(request, 'Estado actualizado exitosamente.')
            return redirect('work_order_edit', order_id=order_id)
        
        # Manejar actualización general
        form = WorkOrderForm(request.POST, instance=work_order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Orden de trabajo actualizada exitosamente.')
            return redirect('dashboard')
    else:
        form = WorkOrderForm(instance=work_order)


    
    # Obtener notas y estado de cancelación
    notes = work_order.workordernote_set.all().order_by('-created_at')
    cancel_note = notes.filter(is_cancel_reason=True).first()
    
    context = {
        'form': form,
        'work_order': work_order,
        'notes': notes,
        'cancel_note': cancel_note,
        'action': 'Editar',
        'status_choices': WorkOrder.STATUS_CHOICES,
        'is_mechanic': hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'mechanic'
    }
    return render(request, 'workshop/admin/work_order_form.html', context)

@login_required
@receptionist_required
def work_order_delete(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    
    if request.method == 'POST':
        cancel_reason = request.POST.get('cancel_reason')
        if cancel_reason:
            work_order.status = 'cancelled'
            work_order.save()
            
            # Create cancellation note
            WorkOrderNote.objects.create(
                work_order=work_order,
                user=request.user,
                note=cancel_reason,
                is_cancel_reason=True
            )
            
            messages.success(request, 'Orden de trabajo cancelada exitosamente.')
        else:
            messages.error(request, 'Debe proporcionar un motivo para la cancelación.')
        return redirect('work_order_list')
    
    return render(request, 'workshop/admin/work_order_confirm_delete.html', {
        'work_order': work_order
    })

# Add this new view function to check availability
@login_required
def check_work_order_availability(request):
    """Check availability for work orders on a specific date"""
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Date is required'}, status=400)

    try:
        check_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        if check_date < timezone.now().date():
            return JsonResponse({
                'time_slots': [],
                'message': 'No se pueden hacer reservas en fechas pasadas'
            })

        # Generate time slots from 9:00 AM to 6:00 PM
        time_slots = []
        start_time = datetime.strptime('09:00', '%H:%M').time()
        end_time = datetime.strptime('18:00', '%H:%M').time()
        
        current_time = start_time
        while current_time <= end_time:
            slot_datetime = timezone.make_aware(datetime.combine(check_date, current_time))
            
            # Skip past times for today
            if check_date == timezone.now().date() and current_time <= timezone.now().time():
                current_time = (datetime.combine(check_date, current_time) + 
                              timedelta(minutes=30)).time()
                continue

            # Check for existing work orders at this time
            existing_orders = WorkOrder.objects.filter(
                estimated_completion=slot_datetime,
                status__in=['pending', 'in_progress']
            )

            # Get assigned mechanics for this time slot
            busy_mechanics = existing_orders.values_list('mechanic', flat=True)
            available_mechanics = UserProfile.objects.filter(role='mechanic').exclude(id__in=busy_mechanics)

            time_slots.append({
                'time': current_time.strftime('%H:%M'),
                'available': available_mechanics.exists(),
                'reason': 'No hay mecánicos disponibles' if not available_mechanics.exists() else None
            })
            
            current_time = (datetime.combine(check_date, current_time) + 
                          timedelta(minutes=30)).time()
        
        return JsonResponse({
            'time_slots': time_slots,
            'message': None if time_slots else 'No hay horarios disponibles para esta fecha'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
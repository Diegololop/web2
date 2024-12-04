from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Product
from ..forms.service_forms import ServiceForm
from ..decorators import admin_required

def service_list_public(request):
    """Vista pública de servicios"""
    services = Product.objects.filter(category='service')
    return render(request, 'workshop/service_list_public.html', {
        'services': services
    })

@login_required
@admin_required
def service_list(request):
    """Vista administrativa de servicios"""
    services = Product.objects.filter(category='service')
    return render(request, 'workshop/admin/service_list.html', {
        'services': services
    })

@login_required
@admin_required
def service_add(request):
    """Agregar nuevo servicio"""
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio creado exitosamente.')
            return redirect('service_list')
    else:
        form = ServiceForm()
    
    return render(request, 'workshop/admin/service_form.html', {
        'form': form,
        'action': 'Crear'
    })

@login_required
@admin_required
def service_edit(request, service_id):
    """Editar servicio existente"""
    service = get_object_or_404(Product, id=service_id, category='service')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado exitosamente.')
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'workshop/admin/service_form.html', {
        'form': form,
        'service': service,
        'action': 'Editar'
    })

@login_required
@admin_required
def service_delete(request, service_id):
    """Eliminar servicio"""
    service = get_object_or_404(Product, id=service_id, category='service')
    
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Servicio eliminado exitosamente.')
        return redirect('service_list')
    
    return render(request, 'workshop/admin/service_confirm_delete.html', {
        'service': service
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ..models import Client
from ..forms import ClientForm

def is_admin(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin')

def is_admin_or_receptionist(user):
    if user.is_superuser:
        return True
    if hasattr(user, 'userprofile'):
        return user.userprofile.role in ['admin', 'receptionist']
    return False

def can_view_work_order(user, work_order):
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'receptionist']):
        return True
    if hasattr(user, 'userprofile') and user.userprofile.role == 'mechanic':
        return work_order.mechanic == user.userprofile
    return False

def can_manage_inventory(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'mechanic'])

@login_required
@user_passes_test(is_admin_or_receptionist)
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'workshop/admin/client_list.html', {'clients': clients})

@login_required
@user_passes_test(is_admin_or_receptionist)
def client_add(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'workshop/admin/client_form.html', {
        'form': form,
        'action': 'Crear'
    })

@login_required
@user_passes_test(is_admin_or_receptionist)
def client_edit(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'workshop/admin/client_form.html', {
        'form': form,
        'client': client,
        'action': 'Editar'
    })

@login_required
@user_passes_test(is_admin)
def client_delete(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        user = client.user
        client.delete()
        user.delete()
        messages.success(request, 'Cliente eliminado exitosamente.')
        return redirect('client_list')
    return render(request, 'workshop/admin/client_confirm_delete.html', {'client': client})
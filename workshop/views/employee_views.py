from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import UserProfile
from ..forms.employee_forms import EmployeeCreationForm, EmployeeEditForm
from ..decorators import admin_required

@login_required
@admin_required
def employee_list(request):
    employees = UserProfile.objects.exclude(role='client')
    return render(request, 'workshop/admin/employee_list.html', {
        'employees': employees
    })

@login_required
@admin_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado creado exitosamente.')
            return redirect('employee_list')
    else:
        form = EmployeeCreationForm()
    
    return render(request, 'workshop/admin/employee_form.html', {
        'form': form,
        'action': 'Crear'
    })

@login_required
@admin_required
def employee_edit(request, employee_id):
    employee = get_object_or_404(UserProfile, id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado exitosamente.')
            return redirect('employee_list')
    else:
        form = EmployeeEditForm(instance=employee)
    
    return render(request, 'workshop/admin/employee_form.html', {
        'form': form,
        'employee': employee,
        'action': 'Editar'
    })

@login_required
@admin_required
def employee_delete(request, employee_id):
    employee = get_object_or_404(UserProfile, id=employee_id)
    
    if request.method == 'POST':
        employee.user.delete()  # This will also delete the profile due to CASCADE
        messages.success(request, 'Empleado eliminado exitosamente.')
        return redirect('employee_list')
    
    return render(request, 'workshop/admin/employee_confirm_delete.html', {
        'employee': employee
    })  
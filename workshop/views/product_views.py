from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ..models import *
from ..forms import *

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


def product_list_public(request):
    products = Product.objects.filter(category='product')
    return render(request, 'workshop/product_list_public.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.filter(category='product')
    return render(request, 'workshop/admin/product_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = 'product'
            product.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'workshop/admin/product_form.html', {
        'form': form,
        'action': 'Crear'
    })

@login_required
@user_passes_test(is_admin)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id, category='product')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'workshop/admin/product_form.html', {
        'form': form,
        'product': product,
        'action': 'Editar'
    })

@login_required
@user_passes_test(is_admin)
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id, category='product')
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('product_list')
    return render(request, 'workshop/admin/product_confirm_delete.html', {'product': product})
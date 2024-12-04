from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import *
from ..forms import *
from django.http import JsonResponse

def can_manage_inventory(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'mechanic'])


@login_required
@user_passes_test(can_manage_inventory)
def inventory_list(request):
    products = Product.objects.filter(category='product').order_by('name')
    search_query = request.GET.get('search', '')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    return render(request, 'workshop/admin/inventory_list.html', {
        'products': products,
        'search_query': search_query
    })

@login_required
@user_passes_test(can_manage_inventory)
def inventory_adjust(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        adjustment = request.POST.get('adjustment')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason')
        
        try:
            quantity = int(quantity)
            if adjustment == 'add':
                product.stock += quantity
            elif adjustment == 'remove':
                if product.stock >= quantity:
                    product.stock -= quantity
                else:
                    messages.error(request, 'No hay suficiente stock disponible.')
                    return redirect('inventory_list')
            
            product.save()
            
            # Registrar el movimiento de inventario
            InventoryMovement.objects.create(
                product=product,
                user=request.user,
                movement_type=adjustment,
                quantity=quantity,
                reason=reason
            )
            
            messages.success(request, f'Stock actualizado exitosamente. Nuevo stock: {product.stock}')
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
        
        return redirect('inventory_list')
    
    return render(request, 'workshop/admin/inventory_adjust.html', {
        'product': product
    })
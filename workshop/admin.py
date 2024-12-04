from django.contrib import admin
from .models import UserProfile, Product, Client, WorkOrder, WorkOrderNote, Reservation

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'duration')
    list_filter = ('category',)
    search_fields = ('name', 'description')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'user__email', 'phone', 'address')

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'mechanic', 'status', 'created_at', 'estimated_completion')
    list_filter = ('status',)
    search_fields = ('client__user__username', 'vehicle_model', 'description')

@admin.register(WorkOrderNote)
class WorkOrderNoteAdmin(admin.ModelAdmin):
    list_display = ('work_order', 'user', 'created_at')
    search_fields = ('work_order__id', 'note')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('client', 'service_date', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('client__user__username', 'description')
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
import re

def validate_password_strength(value):
    if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
        raise ValidationError(
            'La contraseña debe contener al menos una letra mayúscula, una minúscula, '
            'dos dígitos y un carácter especial, y tener al menos 8 caracteres.'
        )

def validate_phone_number(value):
    if not re.match(r'^\+?56\s?9\s?\d{4}\s?\d{4}$', value):
        raise ValidationError(
            'El número de teléfono debe tener el formato: +56 9 XXXX XXXX'
        )

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Cliente'),
        ('mechanic', 'Mecánico'),
        ('receptionist', 'Recepcionista'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

class Client(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='client'
    )
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]{1}$',
                message='Formato de RUT inválido. Debe ser XX.XXX.XXX-X'
            )
        ],
        verbose_name='RUT',
        help_text='Formato: XX.XXX.XXX-X'
    )
    phone = models.CharField(
        max_length=15,
        validators=[validate_phone_number],
        verbose_name='Teléfono',
        help_text='Formato: +56 9 XXXX XXXX'
    )
    address = models.CharField(
        max_length=200,
        verbose_name='Dirección',
        help_text='Ingrese la dirección completa'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    def clean(self):
        # Validar que el RUT tenga el formato correcto
        if self.rut:
            try:
                body, dv = self.rut.split('-')
                body = body.replace('.', '')
                if not body.isdigit():
                    raise ValidationError({'rut': 'El RUT debe contener solo números y un dígito verificador'})
            except ValueError:
                raise ValidationError({'rut': 'Formato de RUT inválido'})

        # Validar el formato del teléfono
        if self.phone and not re.match(r'^\+?56\s?9\s?\d{4}\s?\d{4}$', self.phone):
            raise ValidationError({'phone': 'El número de teléfono debe tener el formato: +56 9 XXXX XXXX'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.rut})"

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('product', 'Producto'),
        ('service', 'Servicio'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='product')
    duration = models.PositiveIntegerField(null=True, blank=True, help_text='Duración estimada en minutos')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    services = models.ManyToManyField(Product)
    service_date = models.DateTimeField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    total_duration = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_totals(self):
        """Calculate total duration and price from selected services"""
        services = self.services.all()
        self.total_duration = sum(service.duration or 0 for service in services)
        self.total_price = sum(service.price for service in services)
        return self.total_duration, self.total_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Calculate totals after saving to handle many-to-many relationship
        self.calculate_totals()
        if self.pk:  # Only update if the instance exists
            Reservation.objects.filter(pk=self.pk).update(
                total_duration=self.total_duration,
                total_price=self.total_price
            )

    def __str__(self):
        return f'Reserva #{self.id} - {self.client.user.get_full_name()}'

    class Meta:
        ordering = ['-service_date']

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_model = models.CharField(max_length=100)
    vehicle_year = models.IntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'Orden #{self.id} - {self.client.user.get_full_name()}'

class WorkOrderNote(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_cancel_reason = models.BooleanField(default=False)

    def __str__(self):
        return f'Nota en Orden #{self.work_order.id} por {self.user.get_full_name()}'

    class Meta:
        ordering = ['-created_at']

class BusinessHours(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Horario de Atención'
        verbose_name_plural = 'Horarios de Atención'
        ordering = ['day']

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_display()}: Cerrado"
        return f"{self.get_day_display()}: {self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"
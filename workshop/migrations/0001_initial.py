# Generated by Django 5.0.1 on 2024-12-04 04:31

import django.core.validators
import django.db.models.deletion
import workshop.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')])),
                ('open_time', models.TimeField()),
                ('close_time', models.TimeField()),
                ('is_closed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Horario de Atención',
                'verbose_name_plural': 'Horarios de Atención',
                'ordering': ['day'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('category', models.CharField(choices=[('product', 'Producto'), ('service', 'Servicio')], default='product', max_length=10)),
                ('duration', models.PositiveIntegerField(blank=True, help_text='Duración estimada en minutos', null=True)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut', models.CharField(help_text='Formato: XX.XXX.XXX-X', max_length=12, unique=True, validators=[django.core.validators.RegexValidator(message='Formato de RUT inválido. Debe ser XX.XXX.XXX-X', regex='^\\d{1,2}\\.\\d{3}\\.\\d{3}[-][0-9kK]{1}$')], verbose_name='RUT')),
                ('phone', models.CharField(help_text='Formato: +56 9 XXXX XXXX', max_length=15, validators=[workshop.models.validate_phone_number], verbose_name='Teléfono')),
                ('address', models.CharField(help_text='Ingrese la dirección completa', max_length=200, verbose_name='Dirección')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_date', models.DateTimeField()),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('confirmed', 'Confirmada'), ('cancelled', 'Cancelada')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('total_duration', models.PositiveIntegerField(default=0)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workshop.client')),
                ('services', models.ManyToManyField(to='workshop.product')),
            ],
            options={
                'ordering': ['-service_date'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('client', 'Cliente'), ('mechanic', 'Mecánico'), ('receptionist', 'Recepcionista'), ('admin', 'Administrador')], max_length=20)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_model', models.CharField(max_length=100)),
                ('vehicle_year', models.IntegerField()),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('in_progress', 'En Proceso'), ('completed', 'Completado'), ('cancelled', 'Cancelado')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('estimated_completion', models.DateTimeField(blank=True, null=True)),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workshop.client')),
                ('mechanic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='workshop.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_cancel_reason', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('work_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workshop.workorder')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

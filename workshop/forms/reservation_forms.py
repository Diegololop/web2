from datetime import datetime, time, timedelta, timezone
from django import forms
from django.core.validators import RegexValidator
from ..models import BusinessHours, Reservation, Product, Client

class ReservationModelForm(forms.ModelForm):
    """Form for managing reservations in admin panel"""
    class Meta:
        model = Reservation
        fields = ['client', 'services', 'service_date', 'description', 'status']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'services': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'service_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['services'].queryset = Product.objects.filter(category='service')
        
        # Si hay una instancia, convertir la fecha a formato datetime-local
        if self.instance.pk and self.instance.service_date:
            self.initial['service_date'] = self.instance.service_date.strftime('%Y-%m-%dT%H:%M')

        for field_name, field in self.fields.items():
            if field_name != 'description':
                field.required = True

    def clean_service_date(self):
        service_date = self.cleaned_data.get('service_date')
        if not service_date:
            raise forms.ValidationError('La fecha y hora son requeridas.')

        # Validar que la fecha no sea en el pasado
        now = timezone.localtime()
        if service_date < now:
            raise forms.ValidationError('La fecha no puede estar en el pasado.')

        # Validar día de la semana y horario de atención
        day_of_week = service_date.weekday()
        try:
            business_hours = BusinessHours.objects.get(day=day_of_week)
            if business_hours.is_closed:
                raise forms.ValidationError(f'No hay atención los {business_hours.get_day_display()}.')
            
            service_time = service_date.time()
            if service_time < business_hours.open_time or service_time > business_hours.close_time:
                raise forms.ValidationError(
                    f'El horario de atención es de {business_hours.open_time.strftime("%H:%M")} '
                    f'a {business_hours.close_time.strftime("%H:%M")}.'
                )
        except BusinessHours.DoesNotExist:
            raise forms.ValidationError('No hay horarios definidos para este día.')

        return service_date

    def clean(self):
        cleaned_data = super().clean()
        services = cleaned_data.get('services')
        service_date = cleaned_data.get('service_date')

        if services and service_date:
            # Calcular duración total y precio
            total_duration = sum(service.duration or 0 for service in services)
            total_price = sum(service.price for service in services)

            # Verificar que la reserva termine dentro del horario de atención
            end_time = service_date + timedelta(minutes=total_duration)
            business_hours = BusinessHours.objects.get(day=service_date.weekday())
            
            closing_datetime = datetime.combine(
                service_date.date(),
                business_hours.close_time,
                tzinfo=service_date.tzinfo
            )

            if end_time > closing_datetime:
                raise forms.ValidationError(
                    'La duración total de los servicios excede el horario de atención.'
                )

            # Agregar los totales al cleaned_data
            cleaned_data['total_duration'] = total_duration
            cleaned_data['total_price'] = total_price

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.total_duration = self.cleaned_data['total_duration']
        instance.total_price = self.cleaned_data['total_price']
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class ReservationForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    services = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(category='service'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )
    service_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        ),
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Descripción adicional (opcional)'
        }),
        required=False
    )

    class Meta:
        model = Reservation
        fields = ['client', 'services', 'service_date', 'description']

    def clean(self):
        cleaned_data = super().clean()
        services = cleaned_data.get('services')
        
        if services:
            total_duration = sum(service.duration or 0 for service in services)
            total_price = sum(service.price for service in services)
            cleaned_data['total_duration'] = total_duration
            cleaned_data['total_price'] = total_price
        
        return cleaned_data

class GuestReservationForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'El nombre es requerido'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'El apellido es requerido'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su apellido'
        })
    )
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'El email es requerido',
            'invalid': 'Por favor ingrese un email válido'
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        error_messages={'required': 'El teléfono es requerido'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 XXXX XXXX'
        })
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]{1}$',
                message='Formato de RUT inválido. Debe ser XX.XXX.XXX-X'
            )
        ],
        error_messages={'required': 'El RUT es requerido'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XX.XXX.XXX-X'
        })
    )
    date = forms.DateField(
        required=True,
        error_messages={'required': 'La fecha es requerida'},
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    time = forms.TimeField(
        required=True,
        error_messages={'required': 'La hora es requerida'},
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Descripción adicional (opcional)'
        })
    )

class ServiceSelectForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Product.objects.filter(category='service'),
        empty_label="Seleccione un servicio",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
from django import forms
from django.core.validators import RegexValidator
from ..models import Client

class ClientForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el apellido'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )
    
    rut = forms.CharField(
        max_length=12,
        required=True,
        label='RUT',
        validators=[
            RegexValidator(
                regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]{1}$',
                message='Formato de RUT inválido. Debe ser XX.XXX.XXX-X'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XX.XXX.XXX-X'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 XXXX XXXX'
        })
    )
    
    address = forms.CharField(
        max_length=200,
        required=True,
        label='Dirección',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la dirección completa'
        })
    )

    class Meta:
        model = Client
        fields = ['rut', 'phone', 'address']

    def save(self, commit=True):
        client = super().save(commit=False)
        if commit:
            # Create or update User
            if not client.user_id:
                from django.contrib.auth.models import User
                user = User.objects.create(
                    username=self.cleaned_data['email'],
                    email=self.cleaned_data['email'],
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    password=User.objects.make_random_password()  # Random password for later activation
                )
                client.user = user
            else:
                client.user.first_name = self.cleaned_data['first_name']
                client.user.last_name = self.cleaned_data['last_name']
                client.user.email = self.cleaned_data['email']
                client.user.save()
            
            client.save()
        return client
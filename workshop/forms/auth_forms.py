from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator, EmailValidator
from ..models import Client


class ClientRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre de Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese un nombre de usuario'
        })
    )
    
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
        validators=[EmailValidator()],
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
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una contraseña'
        })
    )
    
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            'La contraseña debe contener al menos:\n'
            '- 8 caracteres\n'
            '- Una letra mayúscula\n'
            '- Una letra minúscula\n'
            '- Un número\n'
            '- Un carácter especial (@$!%*?&)'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if Client.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Este RUT ya está registrado.')
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address']
            )
        return user
    
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.password_validation import validate_password
from ..models import Client

class ClientActivationForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label='Email',
        validators=[EmailValidator(message='Ingrese un email válido')],
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
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una contraseña'
        }),
        help_text="""
        La contraseña debe contener al menos:
        - 8 caracteres
        - Una letra mayúscula
        - Una letra minúscula
        - Un número
        - Un carácter especial (@$!%*?&)
        """
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Este campo es requerido.')
        
        # Verificar formato de email
        try:
            EmailValidator()(email)
        except forms.ValidationError:
            raise forms.ValidationError('Ingrese un email válido.')
        
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if not password:
            raise forms.ValidationError('Este campo es requerido.')
        
        # Validar requisitos de contraseña
        try:
            validate_password(password)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)

        return password

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        rut = cleaned_data.get('rut')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if email and rut:
            # Verificar que el cliente existe
            try:
                client = Client.objects.get(rut=rut, user__email=email)
                self.instance = client
            except Client.DoesNotExist:
                raise forms.ValidationError('No se encontró un cliente con este RUT y email.')

        if password1 and password2:
            # Verificar que las contraseñas coinciden
            if password1 != password2:
                raise forms.ValidationError({
                    'password2': 'Las contraseñas no coinciden.'
                })

        return cleaned_data

    def save(self):
        if not hasattr(self, 'instance'):
            raise forms.ValidationError('No se encontró el cliente.')
            
        password = self.cleaned_data['password1']
        user = self.instance.user
        user.set_password(password)
        user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nombre de Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre de usuario'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )

    error_messages = {
        'invalid_login': 'Nombre de usuario o contraseña incorrectos.',
        'inactive': 'Esta cuenta está inactiva.',
    }

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )

    error_messages = {
        'invalid_login': 'Email o contraseña incorrectos. Por favor, intente nuevamente.',
        'inactive': 'Esta cuenta está inactiva.',
    }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Este campo es requerido.')
        
        # Verificar formato de email
        try:
            EmailValidator()(username)
        except forms.ValidationError:
            raise forms.ValidationError('Ingrese un email válido.')
        
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Este campo es requerido.')
        return password
from django import forms
from ..models import Product

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'duration', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del servicio'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del servicio'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Precio del servicio'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Duración en minutos'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duration'].required = True
        
    def save(self, commit=True):
        service = super().save(commit=False)
        service.category = 'service'
        service.stock = 999  # Services don't need stock management
        if commit:
            service.save()
        return service
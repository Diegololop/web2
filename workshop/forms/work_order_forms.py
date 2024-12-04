from django import forms
from django.utils import timezone
from ..models import WorkOrder, WorkOrderNote, UserProfile

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['client', 'mechanic', 'vehicle_model', 'vehicle_year', 
                 'description', 'status', 'estimated_completion', 'total_cost']
        widgets = {
            # Tus widgets actuales
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos que pueden ser requeridos
        required_fields = ['client', 'vehicle_model', 'vehicle_year', 'description']
        for field in required_fields:
            self.fields[field].required = True
        
        # Status por defecto
        self.fields['status'].initial = 'pending'
        
        # Filtrar mecánicos 
        self.fields['mechanic'].queryset = UserProfile.objects.filter(role='mechanic')
        self.fields['mechanic'].label_from_instance = lambda obj: f"{obj.user.get_full_name()}"

class WorkOrderNoteForm(forms.ModelForm):
    class Meta:
        model = WorkOrderNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba una nota o actualización'
            })
        }

from django import forms
from .models import Calificacion


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = [
            'ejercicio',
            'mercado',
            'instrumento',
            'fecha_pago',
            'secuencia',
            'origen',
            'descripcion',
            'isfut',
            'factor_ajuste',
        ]

        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }

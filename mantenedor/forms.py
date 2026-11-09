import re

from django import forms
from .models import Calificacion

# Basta con detectar < o > para bloquear etiquetas como <script> o <img>
PATRON_HTML = re.compile(r'[<>]')


def sin_html(valor, nombre_campo):
    # Rechazamos HTML en vez de limpiarlo, así el usuario sabe qué corregir
    if PATRON_HTML.search(valor):
        raise forms.ValidationError(
            f'El campo {nombre_campo} no puede contener etiquetas HTML ni los símbolos < >.'
        )
    return valor


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

    def clean_instrumento(self):
        instrumento = self.cleaned_data.get('instrumento', '').strip()
        if len(instrumento) < 2:
            raise forms.ValidationError(
                'El instrumento debe tener al menos 2 caracteres.'
            )
        return sin_html(instrumento, 'instrumento')

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        return sin_html(descripcion, 'descripción')

    def clean_factor_ajuste(self):
        factor = self.cleaned_data.get('factor_ajuste')
        if factor is not None and factor < 0:
            raise forms.ValidationError(
                'El factor de ajuste no puede ser negativo.'
            )
        return factor

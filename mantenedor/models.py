from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Calificacion(models.Model):

    MERCADOS = [
        ('ACCIONES', 'Acciones'),
        ('CFI', 'CFI'),
        ('FONDOS', 'Fondos Mutuos'),
    ]

    ORIGENES = [
        ('BOLSA', 'Bolsa'),
        ('CORREDOR', 'Corredor'),
        ('SISTEMA', 'Sistema'),
    ]

    ejercicio = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1990, 'El ejercicio no puede ser anterior a 1990.'),
            MaxValueValidator(2100, 'El ejercicio no puede ser posterior a 2100.'),
        ]
    )
    mercado = models.CharField(max_length=20, choices=MERCADOS)
    instrumento = models.CharField(max_length=100)
    fecha_pago = models.DateField()
    secuencia = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'La secuencia debe ser mayor o igual a 1.'),
            MaxValueValidator(999999, 'La secuencia es demasiado grande.'),
        ]
    )
    origen = models.CharField(max_length=20, choices=ORIGENES)

    descripcion = models.CharField(max_length=255, blank=True)
    isfut = models.BooleanField(default=False)

    factor_ajuste = models.DecimalField(
        max_digits=15,
        decimal_places=10,
        default=0,
        validators=[
            MinValueValidator(0, 'El factor de ajuste no puede ser negativo.'),
            MaxValueValidator(99999, 'El factor de ajuste es demasiado grande.'),
        ]
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.instrumento} - {self.ejercicio}"

class RegistroAuditoria(models.Model):
    ACCIONES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
    ]

    usuario = models.CharField(max_length=100)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    instrumento = models.CharField(max_length=100)
    descripcion = models.TextField()
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accion} - {self.instrumento} - {self.fecha}"

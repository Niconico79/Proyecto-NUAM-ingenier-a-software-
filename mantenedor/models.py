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

    ejercicio = models.PositiveIntegerField()
    mercado = models.CharField(max_length=20, choices=MERCADOS)
    instrumento = models.CharField(max_length=100)
    fecha_pago = models.DateField()
    secuencia = models.PositiveIntegerField()
    origen = models.CharField(max_length=20, choices=ORIGENES)

    descripcion = models.CharField(max_length=255, blank=True)
    isfut = models.BooleanField(default=False)

    factor_ajuste = models.DecimalField(
        max_digits=15,
        decimal_places=10,
        default=0
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

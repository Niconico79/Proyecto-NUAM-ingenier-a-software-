from django.contrib import admin
from .models import Calificacion, RegistroAuditoria


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = (
        'ejercicio',
        'instrumento',
        'mercado',
        'fecha_pago',
        'secuencia',
        'origen',
        'factor_ajuste',
    )
    search_fields = ('instrumento',)
    list_filter = ('ejercicio', 'mercado', 'origen')


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = (
        'fecha',
        'usuario',
        'accion',
        'instrumento',
        'descripcion',
    )
    list_filter = ('accion', 'fecha', 'usuario')
    search_fields = ('instrumento', 'usuario', 'descripcion')
    readonly_fields = (
        'usuario',
        'accion',
        'instrumento',
        'descripcion',
        'datos_anteriores',
        'datos_nuevos',
        'fecha',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
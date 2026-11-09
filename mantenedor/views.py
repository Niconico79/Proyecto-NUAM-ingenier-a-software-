
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Calificacion, RegistroAuditoria
from .forms import CalificacionForm


def obtener_datos(calificacion):
    return {
        'ejercicio': calificacion.ejercicio,
        'mercado': calificacion.mercado,
        'instrumento': calificacion.instrumento,
        'fecha_pago': calificacion.fecha_pago.isoformat(),
        'secuencia': calificacion.secuencia,
        'origen': calificacion.origen,
        'descripcion': calificacion.descripcion,
        'isfut': calificacion.isfut,
        'factor_ajuste': str(calificacion.factor_ajuste),
    }


def obtener_usuario(request):
    if request.user.is_authenticated:
        return request.user.username
    return 'Operador'


def inicio(request):
    calificaciones = Calificacion.objects.all().order_by('-ejercicio')

    mercado = request.GET.get('mercado', '')
    ejercicio = request.GET.get('ejercicio', '')

    if mercado:
        calificaciones = calificaciones.filter(mercado=mercado)

    if ejercicio:
        calificaciones = calificaciones.filter(ejercicio=ejercicio)

    ejercicios = (
        Calificacion.objects
        .values_list('ejercicio', flat=True)
        .distinct()
        .order_by('-ejercicio')
    )

    return render(request, 'mantenedor/index.html', {
        'calificaciones': calificaciones,
        'mercados': Calificacion.MERCADOS,
        'ejercicios': ejercicios,
        'mercado_seleccionado': mercado,
        'ejercicio_seleccionado': ejercicio,
    })


def crear_calificacion(request):
    form = CalificacionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        calificacion = form.save()

        RegistroAuditoria.objects.create(
            usuario=obtener_usuario(request),
            accion='CREAR',
            instrumento=calificacion.instrumento,
            descripcion='Se registró una nueva calificación.',
            datos_nuevos=obtener_datos(calificacion)
        )

        messages.success(request, 'Calificación registrada correctamente.')
        return redirect('inicio')

    return render(request, 'mantenedor/formulario.html', {
        'form': form,
        'titulo': 'Registrar calificación'
    })


def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    datos_anteriores = obtener_datos(calificacion)

    form = CalificacionForm(request.POST or None, instance=calificacion)

    if request.method == 'POST' and form.is_valid():
        calificacion = form.save()

        RegistroAuditoria.objects.create(
            usuario=obtener_usuario(request),
            accion='EDITAR',
            instrumento=calificacion.instrumento,
            descripcion='Se modificó una calificación.',
            datos_anteriores=datos_anteriores,
            datos_nuevos=obtener_datos(calificacion)
        )

        messages.success(request, 'Calificación actualizada correctamente.')
        return redirect('inicio')

    return render(request, 'mantenedor/formulario.html', {
        'form': form,
        'titulo': 'Editar calificación'
    })


def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == 'POST':
        datos_anteriores = obtener_datos(calificacion)

        RegistroAuditoria.objects.create(
            usuario=obtener_usuario(request),
            accion='ELIMINAR',
            instrumento=calificacion.instrumento,
            descripcion='Se eliminó una calificación.',
            datos_anteriores=datos_anteriores
        )

        calificacion.delete()
        messages.success(request, 'Calificación eliminada correctamente.')

    return redirect('inicio')

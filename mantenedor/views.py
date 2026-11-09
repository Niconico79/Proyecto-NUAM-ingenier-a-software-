import csv
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Calificacion, RegistroAuditoria
from .forms import CalificacionForm
from .permisos import es_administrador, solo_administradores


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


@login_required(login_url='login')
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
        'puede_modificar': es_administrador(request.user),
    })


@solo_administradores
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


@solo_administradores
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


@solo_administradores
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


@solo_administradores
def importar_csv(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')

        if not archivo:
            messages.error(request, 'Debes seleccionar un archivo CSV.')
            return redirect('importar_csv')

        if not archivo.name.lower().endswith('.csv'):
            messages.error(request, 'El archivo debe tener formato CSV.')
            return redirect('importar_csv')

        if archivo.size > 2 * 1024 * 1024:
            messages.error(request, 'El archivo no puede superar los 2 MB.')
            return redirect('importar_csv')

        try:
            contenido = archivo.read().decode('utf-8-sig')
            lector = csv.DictReader(io.StringIO(contenido))

            columnas_requeridas = {
                'ejercicio', 'mercado', 'instrumento', 'fecha_pago',
                'secuencia', 'origen', 'descripcion', 'isfut',
                'factor_ajuste'
            }

            if not lector.fieldnames or not columnas_requeridas.issubset(
                set(lector.fieldnames)
            ):
                messages.error(
                    request,
                    'El CSV no contiene todas las columnas requeridas.'
                )
                return redirect('importar_csv')

            calificaciones = []
            errores = []

            for numero, fila in enumerate(lector, start=2):
                datos = {
                    clave: (valor or '').strip()
                    for clave, valor in fila.items()
                    if clave is not None
                }

                form = CalificacionForm(datos)

                if form.is_valid():
                    calificaciones.append(form.save(commit=False))
                else:
                    errores.append(
                        f'Fila {numero}: {form.errors.as_text()}'
                    )

            if not calificaciones and not errores:
                errores.append(
                    'El archivo no contiene registros para importar.'
                )

            if errores:
                return render(
                    request,
                    'mantenedor/importar_csv.html',
                    {'errores': errores}
                )

            with transaction.atomic():
                for calificacion in calificaciones:
                    calificacion.save()

                    RegistroAuditoria.objects.create(
                        usuario=obtener_usuario(request),
                        accion='CREAR',
                        instrumento=calificacion.instrumento,
                        descripcion='Calificación importada mediante archivo CSV.',
                        datos_nuevos=obtener_datos(calificacion)
                    )

            messages.success(
                request,
                f'Se importaron correctamente {len(calificaciones)} calificaciones.'
            )
            return redirect('inicio')

        except UnicodeDecodeError:
            messages.error(
                request,
                'No se pudo leer el archivo. Guárdalo con codificación UTF-8.'
            )
            return redirect('importar_csv')

        except Exception:
            # No mostramos el detalle del error al usuario por seguridad
            messages.error(
                request,
                'Ocurrió un error durante la importación. Revisa el formato del archivo.'
            )
            return redirect('importar_csv')

    return render(request, 'mantenedor/importar_csv.html')

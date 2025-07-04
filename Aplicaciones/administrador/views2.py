from email.mime import message
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Equipo, HistorialOperatividad, Mantenimiento, Usuario
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Count, Q
from django.contrib.auth.hashers import make_password,check_password
from django.utils import timezone
# Inicio de la vista principal del tecnico
def inicio2(request):
    hoy = timezone.now().date()
    estados = (
        Equipo.objects.values('estado_operativo')
        .annotate(total=Count('id'))
        .order_by('estado_operativo')
    )
    total_equipos = sum(e['total'] for e in estados)
    estado_colors = {
        "Activo": "#198754",         # bg-success
        "Inactivo": "#6c757d",       # bg-secondary
        "En reparación": "#ffc107",  # bg-warning
        "Obsoleto": "#212529",       # bg-dark
        "Retirado": "#dc3545",       # bg-danger
        "Sin valor": "#adb5bd",      # bg-light
    }
    estados_info = []
    for e in estados:
        nombre = e['estado_operativo'] if e['estado_operativo'] else 'Sin valor'
        color = estado_colors.get(nombre, "#adb5bd")
        porcentaje = int((e['total'] / total_equipos) * 100) if total_equipos else 0
        estados_info.append({
            'nombre': nombre,
            'total': e['total'],
            'color': color,
            'porcentaje': porcentaje,
            'total_equipos': total_equipos
        })
    pendientes_qs = (
        Mantenimiento.objects
        .filter(fecha_realizada__isnull=True)
        .values('equipo__id', 'equipo__nombre')
        .annotate(
            pendientes=Count('id')
        )
        .order_by('-pendientes')[:7]
    )

    equipos_pendientes = []
    for e in pendientes_qs:
        nombre = e['equipo__nombre']
        equipo_id = e['equipo__id']
        realizados = Mantenimiento.objects.filter(equipo_id=equipo_id, fecha_realizada__isnull=False).count()
        equipos_pendientes.append({
            'nombre': nombre,
            'pendientes': e['pendientes'],
            'realizados': realizados,
        })

    return render(request, 'tecnico/inicio2.html', {
        'estados_info': estados_info,
        'total_equipos': total_equipos,
        'equipos_pendientes': equipos_pendientes,
    })

#Perfil de usuario

def perfil_usuario_tecnico(request):
    user=Usuario.objects.get(id=request.session.get('usuario_id'))
    return render(request, 'tecnico/perfil.html', {'user': user})

@csrf_exempt
def perfil_editar_tecnico(request):
    user = Usuario.objects.get(id=request.session.get('usuario_id'))
    if request.method == 'POST':
        user.nombre = request.POST.get('nombre')
        user.correo = request.POST.get('correo')
        user.rol = request.POST.get('rol')
        nueva_contraseña = request.POST.get('nueva_contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')
        if nueva_contraseña and nueva_contraseña != confirmar_contraseña:
            return JsonResponse({'status': 'error', 'message': 'Las contraseñas no coinciden.'})
        if nueva_contraseña:
            user.contraseña_encriptada = make_password(nueva_contraseña)
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Perfil actualizado exitosamente.'})
    return render(request, 'tecnico/perfil_edit.html', {'user': user})

#secion de equipos
def equipo_tecnico(request):
    return render(request, 'tecnico/equipo.html')

def equipo_list_tecnico(request):
    equipos = Equipo.objects.all().order_by('-id')  # Ordena por id descendente
    html = render_to_string('tecnico/tables/equipo_list.html', {'equipos': equipos})
    return JsonResponse({'html': html})

#informacion del euipo mantenimiento y historial operativo
def equipo_info_tecnico(request):
    id = request.GET.get('id')
    equipo = get_object_or_404(Equipo, id=id)
    context = {
        'equipo': equipo,
    }

    return render(request, 'tecnico/info.html', context)
# mantemiento datos
def mantenimiento_list_tecnico(request):
    equipo_id = request.GET.get('equipo_id')
    mantenimientos = Mantenimiento.objects.filter(equipo_id=equipo_id).order_by('-fecha_programada')
    html = render_to_string('tecnico/tables/mantenimiento_list.html', {'mantenimientos': mantenimientos})
    return JsonResponse({'html': html})

def mantenimiento_id_tecnico(request):
    id = request.GET.get('id')
    mantenimiento = get_object_or_404(Mantenimiento, id=id)
    data = {
        'id': mantenimiento.id,
        'equipo_id': mantenimiento.equipo.id,
        'tipo': mantenimiento.tipo,
        'fecha_programada': mantenimiento.fecha_programada,
        'fecha_realizada': mantenimiento.fecha_realizada,
        'tecnico': mantenimiento.tecnico,
        'observaciones': mantenimiento.observaciones,
    }
    return JsonResponse(data)
# marcar mantenimiento realizado y no realizado
@csrf_exempt
def marcar_mantenimiento_realizado(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        mantenimiento = get_object_or_404(Mantenimiento, id=id)
        mantenimiento.fecha_realizada = timezone.now().date()
        mantenimiento.save()
        return JsonResponse({'status': 'success', 'message': 'Mantenimiento marcado como realizado.'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

@csrf_exempt
def marcar_mantenimiento_no_realizado(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        mantenimiento = get_object_or_404(Mantenimiento, id=id)
        mantenimiento.fecha_realizada = None
        mantenimiento.save()
        return JsonResponse({'status': 'success', 'message': 'Mantenimiento marcado como no realizado.'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})
# historial operativo
def historial_list_tecnico(request):
    equipo_id = request.GET.get('equipo_id')
    historial = HistorialOperatividad.objects.filter(equipo_id=equipo_id).order_by('-fecha_hora')
    html = render_to_string('tecnico/tables/historial_list.html', {'historial': historial})
    return JsonResponse({'html': html})

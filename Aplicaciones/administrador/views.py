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

@csrf_exempt
def login(request):
    error = None
    
    if request.method == 'POST':
        correo = request.POST.get('username')
        password = request.POST.get('password')
        try:
            usuario = Usuario.objects.get(correo=correo)
            from django.contrib.auth.hashers import check_password
            if check_password(password, usuario.contraseña_encriptada):
                request.session['usuario_id'] = usuario.id
                if usuario.rol == 'administrador':
                    return redirect('inicio')
                elif usuario.rol == 'tecnico':
                    return redirect('inicio2')
            else:
                error = "Correo o contraseña incorrectos."
        except Usuario.DoesNotExist:
            error = "Correo o contraseña incorrectos."
    return render(request, 'login.html', {'error': error})



@csrf_exempt
def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        rol = request.POST.get('rol')
        contraseña = request.POST.get('contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')

        # Validaciones
        if not (nombre and correo and rol and contraseña and confirmar_contraseña):
            return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'}, status=400)
        if contraseña != confirmar_contraseña:
            return JsonResponse({'status': 'error', 'message': 'Las contraseñas no coinciden.'}, status=400)
        if Usuario.objects.filter(correo=correo).exists():
            return JsonResponse({'status': 'error', 'message': 'El correo ya está registrado.'}, status=400)
        try:
            Usuario.objects.create(
                nombre=nombre,
                correo=correo,
                rol=rol,
                contraseña_encriptada=make_password(contraseña)
            )
            return JsonResponse({'status': 'success', 'message': 'Usuario registrado exitosamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return render(request, 'login.html')

def chart_data(request):
    data_qs = (
        Equipo.objects.values('estado_operativo')
        .annotate(total=Count('id'))
        .order_by('estado_operativo')
    )
    labels = [e['estado_operativo'] if e['estado_operativo'] else 'Sin valor' for e in data_qs]
    data = [e['total'] for e in data_qs]

    # Colores fijos por estado_operativo
    estado_colors = {
        "Activo": "#198754",         # bg-success
        "Inactivo": "#6c757d",       # bg-secondary
        "En reparación": "#ffc107",  # bg-warning
        "Obsoleto": "#212529",       # bg-dark
        "Retirado": "#dc3545",       # bg-danger
        "Sin valor": "#adb5bd",      # bg-light
    }

    colores = [estado_colors.get(label, "#adb5bd") for label in labels]

    return JsonResponse({
        'labels': labels,
        'data': data,
        'colores': colores
    })



def chart_mantenimiento_equipo(request):
    equipo_id = request.GET.get('equipo_id')
    filtro = request.GET.get('filtro', 'tipo')
    if not equipo_id:
        return JsonResponse({'labels': [], 'data': [], 'colores': []})

    if filtro == 'realizada':
        # Realizada: fecha_realizada no es nulo
        data_qs = (
            Mantenimiento.objects
            .filter(equipo_id=equipo_id)
            .annotate(realizada=~Q(fecha_realizada=None))
            .values('realizada')
            .annotate(total=Count('id'))
        )
        labels = ['Realizada' if e['realizada'] else 'No realizada' for e in data_qs]
        data = [e['total'] for e in data_qs]
        colores = ['#198754', '#dc3545']  # Verde y rojo
        # Asegura el orden: Realizada, No realizada
        if len(labels) == 2 and labels[0] == 'No realizada':
            labels.reverse()
            data.reverse()
    else:
        data_qs = (
            Mantenimiento.objects
            .filter(equipo_id=equipo_id)
            .values('tipo')
            .annotate(total=Count('id'))
            .order_by('tipo')
        )
        labels = [e['tipo'] for e in data_qs]
        data = [e['total'] for e in data_qs]
        # Colores por tipo (puedes personalizar)
        tipo_colors = {
            "Preventivo": "#1d7af3",
            "Correctivo": "#f3545d",
            "Predictivo": "#fdaf4b",
        }
        colores = [tipo_colors.get(label, "#adb5bd") for label in labels]

    return JsonResponse({
        'labels': labels,
        'data': data,
        'colores': colores
    })

def inicio(request):
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
    # Equipos con mantenimientos pendientes (no realizados y programados antes de hoy)
    # Equipos con mantenimientos pendientes (no realizados)
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

    return render(request, 'admin/inicio.html', {
        'estados_info': estados_info,
        'total_equipos': total_equipos,
        'equipos_pendientes': equipos_pendientes,
    })

#Perfil de usuario

def perfil_usuario(request):
    user=Usuario.objects.get(id=request.session.get('usuario_id'))
    return render(request, 'admin/perfil.html', {'user': user})

@csrf_exempt
def perfil_editar(request):
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
    return render(request, 'admin/perfil_edit.html', {'user': user})

#secion de equipos
def equipo(request):
    return render(request, 'admin/equipo.html')

def equipo_list(request):
    equipos = Equipo.objects.all().order_by('-id')  # Ordena por id descendente
    html = render_to_string('admin/tables/equipo_list.html', {'equipos': equipos})
    return JsonResponse({'html': html})

@csrf_exempt
def equipo_add(request):
    try:
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            marca = request.POST.get('marca')
            modelo = request.POST.get('modelo')
            serie = request.POST.get('serie')
            ubicacion = request.POST.get('ubicacion')
            fecha_adquisicion = request.POST.get('fechaAdquisicion')
            estado_operativo = request.POST.get('estadoOperativo')
            Equipo.objects.create(
                nombre=nombre,
                tipo=tipo,
                marca=marca,
                modelo=modelo,
                serie=serie,
                ubicacion=ubicacion,
                fecha_adquisicion=fecha_adquisicion,
                estado_operativo=estado_operativo
            )
            return JsonResponse({'status': 'success', 'message': 'Equipo agregado exitosamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt
def equipo_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        equipo = get_object_or_404(Equipo, id=id)
        equipo.delete()
        return JsonResponse({'status': 'success'})

def equipo_id(request):
    id = request.GET.get('id')
    equipo = get_object_or_404(Equipo, id=id)
    data = {
        'id': equipo.id,
        'nombre': equipo.nombre,
        'tipo': equipo.tipo,
        'marca': equipo.marca,
        'modelo': equipo.modelo,
        'serie': equipo.serie,
        'ubicacion': equipo.ubicacion,
        'fecha_adquisicion': equipo.fecha_adquisicion,
        'estado_operativo': equipo.estado_operativo,
    }
    return JsonResponse(data)

@csrf_exempt
def equipo_edit(request):
    try:
        if request.method == 'POST':
            id = request.POST.get('editId')
            equipo = get_object_or_404(Equipo, id=id)
            equipo.nombre = request.POST.get('editNombre')
            equipo.tipo = request.POST.get('editTipo')
            equipo.marca = request.POST.get('editMarca')
            equipo.modelo = request.POST.get('editModelo')
            equipo.serie = request.POST.get('editSerie')
            equipo.ubicacion = request.POST.get('editUbicacion')
            equipo.fecha_adquisicion = request.POST.get('editFechaAdquisicion')
            equipo.estado_operativo = request.POST.get('editEstadoOperativo')
            equipo.save()
            return JsonResponse({'status': 'success', 'message': 'Equipo actualizado exitosamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 

#informacion del euipo mantenimiento y historial operativo
def equipo_info(request):
    id = request.GET.get('id')
    equipo = get_object_or_404(Equipo, id=id)
    context = {
        'equipo': equipo,
    }

    return render(request, 'admin/info.html', context)
# mantemiento datos
def mantenimiento_list(request):
    equipo_id = request.GET.get('equipo_id')
    mantenimientos = Mantenimiento.objects.filter(equipo_id=equipo_id).order_by('-fecha_programada')
    html = render_to_string('admin/tables/mantenimiento_list.html', {'mantenimientos': mantenimientos})
    return JsonResponse({'html': html})

@csrf_exempt
def mantenimiento_add(request):
    try:
        if request.method == 'POST':
            equipo_id = request.POST.get('equipoId')
            tipo = request.POST.get('tipo')
            fecha_programada = request.POST.get('fechaProgramada')
            tecnico = request.POST.get('tecnico')
            observaciones = request.POST.get('observaciones')
            
            equipo = get_object_or_404(Equipo, id=equipo_id)
            Mantenimiento.objects.create(
                equipo=equipo,
                tipo=tipo,
                fecha_programada=fecha_programada,
                tecnico=tecnico,
                observaciones=observaciones
            )
            return JsonResponse({'status': 'success', 'message': 'Mantenimiento agregado exitosamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def mantenimiento_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        mantenimiento = get_object_or_404(Mantenimiento, id=id)
        mantenimiento.delete()
        return JsonResponse({'status': 'success'})

def mantenimiento_id(request):
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
@csrf_exempt
def mantenimiento_edit(request):
    try:
        if request.method == 'POST':
            id = request.POST.get('mantenimientoId')
            mantenimiento = get_object_or_404(Mantenimiento, id=id)
            mantenimiento.tipo = request.POST.get('editTipoMantenimiento')
            mantenimiento.fecha_programada = request.POST.get('editFechaProgramada')
            mantenimiento.fecha_realizada = request.POST.get('editFechaRealizada')
            if mantenimiento.fecha_realizada == '': 
                mantenimiento.fecha_realizada = None
            mantenimiento.tecnico = request.POST.get('editTecnico')
            mantenimiento.observaciones = request.POST.get('editObservaciones')
            mantenimiento.save()
            return JsonResponse({'status': 'success', 'message': 'Mantenimiento actualizado exitosamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# historial operativo
def historial_list(request):
    equipo_id = request.GET.get('equipo_id')
    historial = HistorialOperatividad.objects.filter(equipo_id=equipo_id).order_by('-fecha_hora')
    html = render_to_string('admin/tables/historial_list.html', {'historial': historial})
    return JsonResponse({'html': html})

@csrf_exempt
def historial_add(request):
    try:
        if request.method == 'POST':
            equipo_id = request.POST.get('equipoId')
            estado = request.POST.get('estadoOperativo')
            fecha_hora = request.POST.get('fechaHora')
            
            equipo = get_object_or_404(Equipo, id=equipo_id)
            HistorialOperatividad.objects.create(
                equipo=equipo,
                estado=estado,
                fecha_hora=fecha_hora
            )
            return JsonResponse({'status': 'success', 'message': 'Historial de operatividad agregado exitosamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@csrf_exempt
def historial_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        historial = get_object_or_404(HistorialOperatividad, id=id)
        historial.delete()
        return JsonResponse({'status': 'success'})

def historial_id(request):
    id = request.GET.get('id')
    historial = get_object_or_404(HistorialOperatividad, id=id)
    data = {
        'id': historial.id,
        'equipo_id': historial.equipo.id,
        'estado': historial.estado,
        'fecha_hora': historial.fecha_hora,
    }
    return JsonResponse(data)
@csrf_exempt
def historial_edit(request):
    try:
        if request.method == 'POST':
            id = request.POST.get('historialId')
            historial = get_object_or_404(HistorialOperatividad, id=id)
            historial.estado = request.POST.get('editEstadoOperativo')
            historial.fecha_hora = request.POST.get('editFechaHora')
            historial.save()
            return JsonResponse({'status': 'success', 'message': 'Historial de operatividad actualizado exitosamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


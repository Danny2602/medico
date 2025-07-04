from django.contrib import admin
from django.urls import path
from . import views,views2

urlpatterns = [
    path('',views.login, name='login'),  # Ruta para la vista de login
    path('registro/', views.registro, name='registro'),  # Ruta para la vista de registro
    path('inicio/', views.inicio, name='inicio'),  # Ruta para la vista de inicio
    path('inicio2/', views2.inicio2, name='inicio2'),  # Ruta para la vista de inicio para técnicos
    path('chart-data/', views.chart_data, name='chart_data'),
    path('chart_mantenimiento_equipo/', views.chart_mantenimiento_equipo, name='chart_mantenimiento_equipo'),  # Ruta para la vista de gráfico de mantenimientos por equipo
    #perfil administrador
    path('perfil_usuario/', views.perfil_usuario, name='perfil_usuario'),  # Ruta para la vista de perfil de usuario
    path('perfil_editar/', views.perfil_editar, name='perfil_editar'),  # Ruta para la vista de edición de perfil de usuario
    # perfil tecnico
    path('perfil_usuario_tecnico/', views2.perfil_usuario_tecnico, name='perfil_usuario_tecnico'),  # Ruta para la vista de perfil de usuario técnico
    path('perfil_editar_tecnico/', views2.perfil_editar_tecnico, name='perfil_editar_tecnico'),  # Ruta para la vista de edición de perfil de usuario técnico
    # sección de equipos
    path('equipo/', views.equipo, name='equipo'),  # Ruta para la vista de equipo
    path('equipo_list/', views.equipo_list, name='equipo_list'),  # Ruta para la lista de equipos
    path('equipo_add/', views.equipo_add, name='equipo_add'),  # Ruta para agregar un equipo
    path('equipo_delete/', views.equipo_delete, name='equipo_delete'),  # Ruta para eliminar un equipo
    path('equipo_id/', views.equipo_id, name='equipo_id'),  # Ruta para obtener un equipo por ID
    path('equipo_edit/', views.equipo_edit, name='equipo_edit'),  # Ruta para editar un equipo
    #info del equipo
    path('equipo_info/', views.equipo_info, name='equipo_info'),
    # sección de mantenimientos
    path('mantenimiento_list/', views.mantenimiento_list, name='mantenimiento_list'),  # Ruta para la lista de mantenimientos
    path('mantenimiento_add/', views.mantenimiento_add, name='mantenimiento_add'),  # Ruta para agregar un mantenimiento
    path('mantenimiento_edit/', views.mantenimiento_edit, name='mantenimiento_edit'),  # Ruta para editar un mantenimiento
    path('mantenimiento_delete/', views.mantenimiento_delete, name='mantenimiento_delete'),  # Ruta para eliminar un mantenimiento
    path('mantenimiento_id/', views.mantenimiento_id, name='mantenimiento_id'),  # Ruta para obtener un mantenimiento por ID
    # sección de historial de operatividad
    path('historial_list/', views.historial_list, name='historial_list'),  # Ruta para la lista de historial de operatividad
    path('historial_add/', views.historial_add, name='historial_add'),  # Ruta para agregar un historial de operatividad
    path('historial_edit/', views.historial_edit, name='historial_edit'),  # Ruta para editar un historial de operatividad
    path('historial_delete/', views.historial_delete, name='historial_delete'),  # Ruta para eliminar un historial de operatividad
    path('historial_id/', views.historial_id, name='historial_id'),  # Ruta para obtener un historial de operatividad por ID

    # seccion Equipo para el tecnico
    path('equipo_tecnico/', views2.equipo_tecnico, name='equipo_tecnico'),  # Ruta para la vista de equipo para técnicos
    path('equipo_list_tecnico/', views2.equipo_list_tecnico, name='equipo_list_tecnico'),  # Ruta para la lista de equipos para técnicos
    # equipo info tecnico
    path('equipo_info_tecnico/', views2.equipo_info_tecnico, name='equipo_info_tecnico'),  # Ruta para obtener información del equipo para técnicos
    # mantenimiento tecnico
    path('mantenimiento_list_tecnico/', views2.mantenimiento_list_tecnico, name='mantenimiento_list_tecnico'),  # Ruta para la lista de mantenimientos para técnicos
    path('mantenimiento_id_tecnico/', views2.mantenimiento_id_tecnico, name='mantenimiento_id_tecnico'),  # Ruta para obtener un mantenimiento por ID para técnicos
    path('marcar_mantenimiento_realizado/', views2.marcar_mantenimiento_realizado, name='marcar_mantenimiento_realizado'),  # Ruta para marcar un mantenimiento como realizado para técnicos
    path('marcar_mantenimiento_no_realizado/', views2.marcar_mantenimiento_no_realizado, name='marcar_mantenimiento_no_realizado'),  # Ruta para marcar un mantenimiento como no realizado para técnicos
    # historial tecnico
    path('historial_list_tecnico/', views2.historial_list_tecnico, name='historial_list_tecnico'),  # Ruta para la lista de historial de operatividad para técnicos
]

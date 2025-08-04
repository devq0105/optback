from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # URLs para pacientes
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('pacientes/crear/', views.crear_paciente, name='crear_paciente'), 
    path('pacientes/<int:pk>/', views.obtener_paciente, name='obtener_paciente'),
    path('pacientes/<int:pk>/actualizar/', views.actualizar_paciente, name='actualizar_paciente'),
    path('pacientes/<int:pk>/eliminar/', views.eliminar_paciente, name='eliminar_paciente'),
    path('pacientes/<int:pk>/activar/', views.activar_paciente, name='activar_paciente'),
    path('pacientes/buscar/<str:codigo>/', views.buscar_paciente_por_codigo, name='buscar_paciente_por_codigo'),
    
    # URLs para citas médicas
    path('citas/', views.listar_citas, name='listar_citas'),
    path('citas/crear/', views.crear_cita, name='crear_cita'),
    path('citas/<int:pk>/', views.obtener_cita, name='obtener_cita'),
    path('citas/<int:pk>/actualizar/', views.actualizar_cita, name='actualizar_cita'),
    path('citas/<int:pk>/eliminar/', views.eliminar_cita, name='eliminar_cita'),
    path('citas/<int:pk>/cambiar-estado/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
    path('citas/<int:pk>/reasignar-doctor/', views.reasignar_doctor, name='reasignar_doctor'),
    path('citas/doctor/<int:doctor_id>/', views.citas_por_doctor, name='citas_por_doctor'),
    path('citas/paciente/<int:paciente_id>/', views.citas_por_paciente, name='citas_por_paciente'),
    
    # URLs para diagnósticos
    path('diagnosticos/', views.listar_diagnosticos, name='listar_diagnosticos'),
    path('diagnosticos/crear/', views.crear_diagnostico, name='crear_diagnostico'),
    path('diagnosticos/<int:pk>/', views.obtener_diagnostico, name='obtener_diagnostico'),
    path('diagnosticos/<int:pk>/actualizar/', views.actualizar_diagnostico, name='actualizar_diagnostico'),
    path('diagnosticos/<int:pk>/eliminar/', views.eliminar_diagnostico, name='eliminar_diagnostico'),
    path('diagnosticos/paciente/<int:paciente_id>/', views.diagnosticos_por_paciente, name='diagnosticos_por_paciente'),
    path('diagnosticos/recordatorios/', views.recordatorios_pendientes, name='recordatorios_pendientes'),
    path('diagnosticos/<int:pk>/recordatorio-enviado/', views.marcar_recordatorio_enviado, name='marcar_recordatorio_enviado'),
    path('diagnosticos/estadisticas/', views.estadisticas_diagnosticos, name='estadisticas_diagnosticos'),
    path('diagnosticos/estructura-datos-clinicos/', views.estructura_datos_clinicos, name='estructura_datos_clinicos'),
    path('diagnosticos/validar-estructura/', views.validar_estructura_datos_clinicos, name='validar_estructura_datos_clinicos'),
] 
from django.contrib import admin
from .models import Paciente, CitaMedica, Diagnostico

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_paciente', 'nombre_completo', 'telefono', 
        'correo', 'genero', 'sucursal', 'usuario_registro', 'activo', 'creado_en'
    ]
    list_filter = ['genero', 'activo', 'sucursal', 'creado_en']
    search_fields = ['nombre_completo', 'codigo_paciente', 'correo', 'telefono']
    readonly_fields = ['codigo_paciente', 'creado_en', 'actualizado_en']
    list_per_page = 25
    date_hierarchy = 'creado_en'
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_completo', 'fecha_nacimiento', 'genero')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'telefono', 'correo')
        }),
        ('Información del Sistema', {
            'fields': ('codigo_paciente', 'usuario_registro', 'sucursal', 'activo')
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario_registro', 'sucursal')


@admin.register(CitaMedica)
class CitaMedicaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'paciente', 'fecha_hora', 'estado', 'doctor_asignado', 
        'sucursal', 'usuario_creacion', 'activo', 'creado_en'
    ]
    list_filter = ['estado', 'activo', 'sucursal', 'doctor_asignado', 'fecha_hora', 'creado_en']
    search_fields = [
        'paciente__nombre_completo', 'paciente__codigo_paciente',
        'doctor_asignado__nombre_completo', 'comentarios'
    ]
    readonly_fields = ['creado_en', 'actualizado_en']
    list_per_page = 25
    date_hierarchy = 'fecha_hora'
    
    fieldsets = (
        ('Información de la Cita', {
            'fields': ('paciente', 'fecha_hora', 'estado', 'comentarios')
        }),
        ('Asignaciones', {
            'fields': ('doctor_asignado', 'usuario_creacion', 'sucursal')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas del Sistema', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'paciente', 'doctor_asignado', 'usuario_creacion', 'sucursal'
        )
    
    def save_model(self, request, obj, form, change):
        # Si es una nueva cita y no tiene usuario_creacion, asignar el usuario actual
        if not change and not obj.usuario_creacion:
            obj.usuario_creacion = request.user
        super().save_model(request, obj, form, change)



@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'paciente', 'fecha_hora_consulta', 'tipo_lente', 
        'proximo_control', 'remision_oftalmologica', 'recordatorio_enviado',
        'usuario_creacion', 'sucursal', 'activo', 'creado_en'
    ]
    list_filter = [
        'tipo_lente', 'material_lente', 'filtro_lente', 'remision_oftalmologica',
        'recordatorio_enviado', 'activo', 'sucursal', 'fecha_hora_consulta', 
        'proximo_control', 'creado_en'
    ]
    search_fields = [
        'paciente__nombre_completo', 'paciente__codigo_paciente',
        'datos_clinicos', 'comentario', 'observaciones_adicionales'
    ]
    readonly_fields = ['creado_en', 'actualizado_en']
    list_per_page = 25
    date_hierarchy = 'fecha_hora_consulta'
    
    fieldsets = (
        ('Información General', {
            'fields': ('paciente', 'fecha_hora_consulta', 'comentario', 'sucursal')
        }),
        ('Datos Clínicos (JSON)', {
            'fields': ('datos_clinicos',),
            'description': 'Datos clínicos en formato JSON. Estructura flexible para todos los campos del examen.',
            'classes': ('wide',)
        }),
        ('Prescripción de Lentes', {
            'fields': ('tipo_lente', 'material_lente', 'filtro_lente'),
        }),
        ('Seguimiento', {
            'fields': (
                'proximo_control', 'recordatorio_enviado', 'remision_oftalmologica',
                'observaciones_adicionales'
            )
        }),
        ('Información del Sistema', {
            'fields': ('usuario_creacion', 'activo')
        }),
        ('Fechas del Sistema', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'paciente', 'usuario_creacion', 'sucursal'
        )
    
    def save_model(self, request, obj, form, change):
        # Si es un nuevo diagnóstico y no tiene usuario_creacion, asignar el usuario actual
        if not change and not obj.usuario_creacion:
            obj.usuario_creacion = request.user
        super().save_model(request, obj, form, change)

# Register your models here.

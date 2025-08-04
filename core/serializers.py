from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Paciente, CitaMedica, Diagnostico
from users.models import Sucursal
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime

Usuario = get_user_model()

class PacienteSerializer(serializers.ModelSerializer):
    usuario_registro_nombre = serializers.CharField(source='usuario_registro.nombre_completo', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    genero_display = serializers.CharField(source='get_genero_display', read_only=True)
    
    class Meta:
        model = Paciente
        fields = [
            'id', 'nombre_completo', 'direccion', 'fecha_nacimiento', 
            'genero', 'genero_display', 'telefono', 'correo', 
            'codigo_paciente', 'usuario_registro', 'usuario_registro_nombre',
            'sucursal', 'sucursal_nombre', 'activo', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['codigo_paciente', 'creado_en', 'actualizado_en']
        extra_kwargs = {
            'nombre_completo': {
                'error_messages': {
                    'blank': 'Error: El nombre completo es requerido',
                    'required': 'Error: El nombre completo es requerido'
                }
            },
            'correo': {
                'error_messages': {
                    'invalid': 'Error: Ingrese un correo electrónico válido'
                }
            }
        }

    def validate_telefono(self, value):
        if value and not value.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise serializers.ValidationError("Error: El teléfono solo debe contener números, espacios, guiones y el signo +")
        if value and len(value.replace('+', '').replace(' ', '').replace('-', '')) < 10:
            raise serializers.ValidationError("Error: El teléfono debe tener al menos 10 dígitos")
        return value

    def validate_correo(self, value):
        if value and Paciente.objects.filter(correo=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Error: Ya existe un paciente con este correo electrónico")
        return value

    def validate_nombre_completo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Error: El nombre completo es requerido")
        return value.strip()

class PacienteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = [
            'nombre_completo', 'direccion', 'fecha_nacimiento', 
            'genero', 'telefono', 'correo', 'sucursal'
        ]
        extra_kwargs = {
            'nombre_completo': {
                'error_messages': {
                    'blank': 'Error: El nombre completo es requerido',
                    'required': 'Error: El nombre completo es requerido'
                }
            },
            'correo': {
                'error_messages': {
                    'invalid': 'Error: Ingrese un correo electrónico válido'
                }
            }
        }

    def validate_telefono(self, value):
        if value and not value.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise serializers.ValidationError("Error: El teléfono solo debe contener números, espacios, guiones y el signo +")
        if value and len(value.replace('+', '').replace(' ', '').replace('-', '')) < 10:
            raise serializers.ValidationError("Error: El teléfono debe tener al menos 10 dígitos")
        return value

    def validate_correo(self, value):
        if value and Paciente.objects.filter(correo=value).exists():
            raise serializers.ValidationError("Error: Ya existe un paciente con este correo electrónico")
        return value

    def validate_nombre_completo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Error: El nombre completo es requerido")
        return value.strip()

    def create(self, validated_data):
        # Asignar el usuario que está creando el paciente
        request = self.context.get('request')
        if request and request.user:
            validated_data['usuario_registro'] = request.user
        
        return super().create(validated_data)

class PacienteListSerializer(serializers.ModelSerializer):
    usuario_registro_nombre = serializers.CharField(source='usuario_registro.nombre_completo', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    genero_display = serializers.CharField(source='get_genero_display', read_only=True)
    
    class Meta:
        model = Paciente
        fields = [
            'id', 'nombre_completo', 'telefono', 'correo', 
            'codigo_paciente', 'usuario_registro_nombre',
            'sucursal_nombre', 'genero_display', 'activo', 'creado_en'
        ]


class CitaMedicaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    paciente_codigo = serializers.CharField(source='paciente.codigo_paciente', read_only=True)
    doctor_nombre = serializers.CharField(source='doctor_asignado.nombre_completo', read_only=True)
    usuario_creacion_nombre = serializers.CharField(source='usuario_creacion.nombre_completo', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    # Campos calculados para validar transiciones de estado
    puede_confirmar = serializers.BooleanField(read_only=True)
    puede_reagendar = serializers.BooleanField(read_only=True)
    puede_cancelar = serializers.BooleanField(read_only=True)
    puede_iniciar = serializers.BooleanField(read_only=True)
    puede_finalizar = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CitaMedica
        fields = [
            'id', 'paciente', 'paciente_nombre', 'paciente_codigo',
            'fecha_hora', 'estado', 'estado_display', 'comentarios',
            'doctor_asignado', 'doctor_nombre', 'usuario_creacion', 
            'usuario_creacion_nombre', 'sucursal', 'sucursal_nombre',
            'puede_confirmar', 'puede_reagendar', 'puede_cancelar', 
            'puede_iniciar', 'puede_finalizar', 'activo', 
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']
        extra_kwargs = {
            'fecha_hora': {
                'error_messages': {
                    'required': 'Error: La fecha y hora son requeridas',
                    'invalid': 'Error: Formato de fecha y hora inválido'
                }
            }
        }

    def validate_fecha_hora(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Error: La fecha y hora de la cita debe ser futura")
        return value

    def validate(self, data):
        # Validar que el paciente esté activo
        if 'paciente' in data and not data['paciente'].activo:
            raise serializers.ValidationError({
                'paciente': 'Error: No se puede crear una cita para un paciente inactivo'
            })
        
        # Validar que el doctor esté activo (si se asigna uno)
        if 'doctor_asignado' in data and data['doctor_asignado'] and not data['doctor_asignado'].is_active:
            raise serializers.ValidationError({
                'doctor_asignado': 'Error: No se puede asignar un doctor inactivo'
            })
        
        return data


class CitaMedicaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitaMedica
        fields = [
            'paciente', 'fecha_hora', 'comentarios', 
            'doctor_asignado', 'sucursal'
        ]
        extra_kwargs = {
            'fecha_hora': {
                'error_messages': {
                    'required': 'Error: La fecha y hora son requeridas',
                    'invalid': 'Error: Formato de fecha y hora inválido'
                }
            }
        }

    def validate_fecha_hora(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Error: La fecha y hora de la cita debe ser futura")
        return value

    def validate(self, data):
        # Validar que el paciente esté activo
        if not data['paciente'].activo:
            raise serializers.ValidationError({
                'paciente': 'Error: No se puede crear una cita para un paciente inactivo'
            })
        
        # Validar que el doctor esté activo (si se asigna uno)
        if data.get('doctor_asignado') and not data['doctor_asignado'].is_active:
            raise serializers.ValidationError({
                'doctor_asignado': 'Error: No se puede asignar un doctor inactivo'
            })
        
        return data

    def create(self, validated_data):
        # Asignar el usuario que está creando la cita
        request = self.context.get('request')
        if request and request.user:
            validated_data['usuario_creacion'] = request.user
        
        return super().create(validated_data)


class CitaMedicaListSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    paciente_codigo = serializers.CharField(source='paciente.codigo_paciente', read_only=True)
    doctor_nombre = serializers.CharField(source='doctor_asignado.nombre_completo', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = CitaMedica
        fields = [
            'id', 'paciente_nombre', 'paciente_codigo', 'fecha_hora',
            'estado', 'estado_display', 'doctor_nombre', 'sucursal_nombre',
            'creado_en'
        ]


class CitaMedicaCambioEstadoSerializer(serializers.Serializer):
    """Serializer para cambios de estado de cita"""
    nuevo_estado = serializers.ChoiceField(choices=CitaMedica.ESTADO_CHOICES)
    comentarios = serializers.CharField(required=False, allow_blank=True)
    nueva_fecha_hora = serializers.DateTimeField(required=False, allow_null=True)
    nuevo_doctor = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )

    def validate_nueva_fecha_hora(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Error: La nueva fecha y hora debe ser futura")
        return value

    def validate(self, data):
        nuevo_estado = data.get('nuevo_estado')
        
        # Si es reagendada, debe tener nueva fecha
        if nuevo_estado == 'reagendada' and not data.get('nueva_fecha_hora'):
            raise serializers.ValidationError({
                'nueva_fecha_hora': 'Error: Debe proporcionar una nueva fecha y hora para reagendar'
            })
        
        return data


class DiagnosticoSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    paciente_codigo = serializers.CharField(source='paciente.codigo_paciente', read_only=True)
    usuario_creacion_nombre = serializers.CharField(source='usuario_creacion.nombre_completo', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    
    # Campos calculados
    tipo_lente_display = serializers.CharField(source='get_tipo_lente_display', read_only=True)
    material_lente_display = serializers.CharField(source='get_material_lente_display', read_only=True)
    filtro_lente_display = serializers.CharField(source='get_filtro_lente_display', read_only=True)
    necesita_recordatorio = serializers.BooleanField(read_only=True)
    dias_hasta_proximo_control = serializers.IntegerField(read_only=True)
    
    # Campos individuales de datos clínicos (para compatibilidad)
    rx_en_uso = serializers.CharField(source='rx_en_uso', read_only=True)
    antecedentes_medicos = serializers.CharField(source='antecedentes_medicos', read_only=True)
    sintomas_signos = serializers.CharField(source='sintomas_signos', read_only=True)
    analisis_panoramico = serializers.CharField(source='analisis_panoramico', read_only=True)
    examen_ojo_derecho = serializers.CharField(source='examen_ojo_derecho', read_only=True)
    examen_ojo_izquierdo = serializers.CharField(source='examen_ojo_izquierdo', read_only=True)
    analisis_pantoscopico = serializers.CharField(source='analisis_pantoscopico', read_only=True)
    analisis_vertice = serializers.CharField(source='analisis_vertice', read_only=True)
    anamnesis_paciente = serializers.CharField(source='anamnesis_paciente', read_only=True)
    hallazgos_encontrados = serializers.CharField(source='hallazgos_encontrados', read_only=True)
    diagnostico_tratamiento = serializers.CharField(source='diagnostico_tratamiento', read_only=True)
    retinoscopia = serializers.CharField(source='retinoscopia', read_only=True)
    agudeza_visual = serializers.CharField(source='agudeza_visual', read_only=True)
    afinacion_subjetiva = serializers.CharField(source='afinacion_subjetiva', read_only=True)
    rx_final = serializers.CharField(source='rx_final', read_only=True)
    
    class Meta:
        model = Diagnostico
        fields = [
            'id', 'paciente', 'paciente_nombre', 'paciente_codigo',
            
            # Campo JSON principal
            'datos_clinicos',
            
            # Campos individuales (solo lectura para compatibilidad)
            'rx_en_uso', 'antecedentes_medicos', 'sintomas_signos', 'analisis_panoramico',
            'examen_ojo_derecho', 'examen_ojo_izquierdo', 'analisis_pantoscopico', 'analisis_vertice',
            'anamnesis_paciente', 'hallazgos_encontrados', 'diagnostico_tratamiento', 'retinoscopia',
            'agudeza_visual', 'afinacion_subjetiva', 'rx_final',
            
            # Información de lentes
            'tipo_lente', 'tipo_lente_display', 'material_lente', 'material_lente_display',
            'filtro_lente', 'filtro_lente_display',
            
            # Controles y seguimiento
            'proximo_control', 'recordatorio_enviado', 'remision_oftalmologica', 'observaciones_adicionales',
            'necesita_recordatorio', 'dias_hasta_proximo_control',
            
            # Información general
            'comentario', 'fecha_hora_consulta', 'usuario_creacion', 'usuario_creacion_nombre',
            'sucursal', 'sucursal_nombre', 'activo', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']
        extra_kwargs = {
            'fecha_hora_consulta': {
                'error_messages': {
                    'required': 'Error: La fecha y hora de la consulta son requeridas',
                    'invalid': 'Error: Formato de fecha y hora inválido'
                }
            },
            'datos_clinicos': {
                'help_text': 'Datos clínicos en formato JSON. Estructura flexible para campos como rx_en_uso, antecedentes_medicos, etc.'
            }
        }

    def validate(self, data):
        # Validar que el paciente esté activo
        if 'paciente' in data and not data['paciente'].activo:
            raise serializers.ValidationError({
                'paciente': 'Error: No se puede crear un diagnóstico para un paciente inactivo'
            })
        
        return data


class DiagnosticoCreateSerializer(serializers.ModelSerializer):
    # Campos individuales opcionales para facilitar el uso
    rx_en_uso = serializers.CharField(required=False, allow_blank=True, write_only=True)
    antecedentes_medicos = serializers.CharField(required=False, allow_blank=True, write_only=True)
    sintomas_signos = serializers.CharField(required=False, allow_blank=True, write_only=True)
    analisis_panoramico = serializers.CharField(required=False, allow_blank=True, write_only=True)
    examen_ojo_derecho = serializers.CharField(required=False, allow_blank=True, write_only=True)
    examen_ojo_izquierdo = serializers.CharField(required=False, allow_blank=True, write_only=True)
    analisis_pantoscopico = serializers.CharField(required=False, allow_blank=True, write_only=True)
    analisis_vertice = serializers.CharField(required=False, allow_blank=True, write_only=True)
    anamnesis_paciente = serializers.CharField(required=False, allow_blank=True, write_only=True)
    hallazgos_encontrados = serializers.CharField(required=False, allow_blank=True, write_only=True)
    diagnostico_tratamiento = serializers.CharField(required=False, allow_blank=True, write_only=True)
    retinoscopia = serializers.CharField(required=False, allow_blank=True, write_only=True)
    agudeza_visual = serializers.CharField(required=False, allow_blank=True, write_only=True)
    afinacion_subjetiva = serializers.CharField(required=False, allow_blank=True, write_only=True)
    rx_final = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    class Meta:
        model = Diagnostico
        fields = [
            'paciente', 'datos_clinicos', 'tipo_lente', 'material_lente',
            'filtro_lente', 'proximo_control', 'remision_oftalmologica', 'observaciones_adicionales',
            'comentario', 'fecha_hora_consulta', 'sucursal',
            # Campos individuales
            'rx_en_uso', 'antecedentes_medicos', 'sintomas_signos', 'analisis_panoramico',
            'examen_ojo_derecho', 'examen_ojo_izquierdo', 'analisis_pantoscopico', 'analisis_vertice',
            'anamnesis_paciente', 'hallazgos_encontrados', 'diagnostico_tratamiento', 'retinoscopia',
            'agudeza_visual', 'afinacion_subjetiva', 'rx_final'
        ]
        extra_kwargs = {
            'fecha_hora_consulta': {
                'error_messages': {
                    'required': 'Error: La fecha y hora de la consulta son requeridas',
                    'invalid': 'Error: Formato de fecha y hora inválido'
                }
            },
            'datos_clinicos': {
                'required': False,
                'help_text': 'Datos clínicos en formato JSON. Si se proporciona, tiene prioridad sobre los campos individuales.'
            }
        }

    def validate(self, data):
        # Validar que el paciente esté activo
        if not data['paciente'].activo:
            raise serializers.ValidationError({
                'paciente': 'Error: No se puede crear un diagnóstico para un paciente inactivo'
            })
        
        # Validar que la fecha de próximo control sea futura
        if data.get('proximo_control') and data['proximo_control'] <= timezone.now().date():
            raise serializers.ValidationError({
                'proximo_control': 'Error: La fecha del próximo control debe ser futura'
            })
        
        return data

    def create(self, validated_data):
        # Asignar el usuario que está creando el diagnóstico
        request = self.context.get('request')
        if request and request.user:
            validated_data['usuario_creacion'] = request.user
        
        # Extraer campos individuales de datos clínicos
        campos_clinicos_individuales = {}
        for campo in Diagnostico.get_campos_clinicos_disponibles():
            if campo in validated_data:
                campos_clinicos_individuales[campo] = validated_data.pop(campo)
        
        # Si se enviaron campos individuales, construir o actualizar el JSON
        if campos_clinicos_individuales:
            if 'datos_clinicos' not in validated_data:
                validated_data['datos_clinicos'] = {}
            
            # Los campos individuales se combinan con datos_clinicos existente
            validated_data['datos_clinicos'].update(campos_clinicos_individuales)
        
        # Si no hay datos_clinicos, inicializar como diccionario vacío
        if 'datos_clinicos' not in validated_data:
            validated_data['datos_clinicos'] = {}
        
        return super().create(validated_data)


class DiagnosticoListSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    paciente_codigo = serializers.CharField(source='paciente.codigo_paciente', read_only=True)
    usuario_creacion_nombre = serializers.CharField(source='usuario_creacion.nombre_completo', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    tipo_lente_display = serializers.CharField(source='get_tipo_lente_display', read_only=True)
    necesita_recordatorio = serializers.BooleanField(read_only=True)
    dias_hasta_proximo_control = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Diagnostico
        fields = [
            'id', 'paciente_nombre', 'paciente_codigo', 'fecha_hora_consulta',
            'rx_final', 'tipo_lente_display', 'proximo_control', 'necesita_recordatorio',
            'dias_hasta_proximo_control', 'remision_oftalmologica', 'usuario_creacion_nombre',
            'sucursal_nombre', 'creado_en'
        ]


class DiagnosticoResumenSerializer(serializers.ModelSerializer):
    """Serializer para mostrar resumen de diagnósticos en el perfil del paciente"""
    usuario_creacion_nombre = serializers.CharField(source='usuario_creacion.nombre_completo', read_only=True)
    tipo_lente_display = serializers.CharField(source='get_tipo_lente_display', read_only=True)
    
    class Meta:
        model = Diagnostico
        fields = [
            'id', 'fecha_hora_consulta', 'rx_final', 'tipo_lente_display',
            'proximo_control', 'remision_oftalmologica', 'usuario_creacion_nombre', 'creado_en'
        ]


class RecordatorioSerializer(serializers.Serializer):
    """Serializer para gestión de recordatorios"""
    diagnostico_id = serializers.IntegerField()
    paciente_nombre = serializers.CharField(read_only=True)
    proximo_control = serializers.DateField(read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    contacto_paciente = serializers.CharField(read_only=True) 
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from users.models import Sucursal

Usuario = get_user_model()

class Paciente(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    nombre_completo = models.CharField(_('nombre completo'), max_length=255)
    direccion = models.TextField(_('dirección'), blank=True)
    fecha_nacimiento = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    genero = models.CharField(_('género'), max_length=1, choices=GENERO_CHOICES, blank=True)
    telefono = models.CharField(_('teléfono'), max_length=20, blank=True)
    correo = models.EmailField(_('correo electrónico'), blank=True)
    codigo_paciente = models.CharField(_('código de paciente'), max_length=20, unique=True, blank=True)
    usuario_registro = models.ForeignKey(
        Usuario,
        verbose_name=_('usuario de registro'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='pacientes_registrados'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name=_('sucursal'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='pacientes'
    )
    activo = models.BooleanField(_('activo'), default=True)
    creado_en = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    actualizado_en = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('paciente')
        verbose_name_plural = _('pacientes')
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.codigo_paciente} - {self.nombre_completo}"

    def _generar_codigo_paciente(self):
        """Genera un código único para el paciente"""
        from django.db.models import Max
        
        # Obtener el último código numérico
        ultimo_paciente = Paciente.objects.aggregate(
            Max('codigo_paciente')
        )['codigo_paciente__max']
        
        if ultimo_paciente:
            try:
                # Extraer el número del código (ej: VOR-00001 -> 1)
                numero = int(ultimo_paciente.split('-')[1])
                nuevo_numero = numero + 1
            except (ValueError, IndexError):
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        # Formatear el código con padding de ceros
        return f"VOR-{nuevo_numero:05d}"

    def save(self, *args, **kwargs):
        if not self.codigo_paciente:
            self.codigo_paciente = self._generar_codigo_paciente()
        super().save(*args, **kwargs)


class CitaMedica(models.Model):
    ESTADO_CHOICES = [
        ('creada', 'Creada'),
        ('confirmada', 'Confirmada'),
        ('reagendada', 'Reagendada'),
        ('cancelada', 'Cancelada'),
        ('en_progreso', 'En progreso'),
        ('finalizada', 'Finalizada'),
    ]
    
    paciente = models.ForeignKey(
        Paciente,
        verbose_name=_('paciente'),
        on_delete=models.CASCADE,
        related_name='citas'
    )
    fecha_hora = models.DateTimeField(_('fecha y hora'))
    estado = models.CharField(
        _('estado de la cita'),
        max_length=20,
        choices=ESTADO_CHOICES,
        default='creada'
    )
    comentarios = models.TextField(_('comentarios'), blank=True)
    doctor_asignado = models.ForeignKey(
        Usuario,
        verbose_name=_('doctor asignado'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas_como_doctor'
    )
    usuario_creacion = models.ForeignKey(
        Usuario,
        verbose_name=_('usuario de creación'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='citas_creadas'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name=_('sucursal'),
        on_delete=models.CASCADE,
        related_name='citas'
    )
    activo = models.BooleanField(_('activo'), default=True)
    creado_en = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    actualizado_en = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('cita médica')
        verbose_name_plural = _('citas médicas')
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['estado']),
            models.Index(fields=['paciente', 'fecha_hora']),
        ]

    def __str__(self):
        return f"Cita - {self.paciente.nombre_completo} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

    @property
    def puede_confirmar(self):
        """Verifica si la cita puede ser confirmada"""
        return self.estado in ['creada', 'reagendada']

    @property
    def puede_reagendar(self):
        """Verifica si la cita puede ser reagendada"""
        return self.estado in ['creada', 'confirmada']

    @property
    def puede_cancelar(self):
        """Verifica si la cita puede ser cancelada"""
        return self.estado in ['creada', 'confirmada', 'reagendada']

    @property
    def puede_iniciar(self):
        """Verifica si la cita puede iniciarse"""
        return self.estado == 'confirmada'

    @property
    def puede_finalizar(self):
        """Verifica si la cita puede finalizarse"""
        return self.estado == 'en_progreso'


class Diagnostico(models.Model):
    TIPO_LENTE_CHOICES = [
        ('monofocal', 'Monofocal'),
        ('bifocal', 'Bifocal'),
        ('progresivo', 'Progresivo'),
        ('ocupacional', 'Ocupacional'),
        ('contacto', 'Lente de Contacto'),
    ]
    
    MATERIAL_LENTE_CHOICES = [
        ('cr39', 'CR-39'),
        ('policarbonato', 'Policarbonato'),
        ('trivex', 'Trivex'),
        ('alto_indice', 'Alto Índice'),
        ('mineral', 'Mineral'),
    ]
    
    FILTRO_LENTE_CHOICES = [
        ('ninguno', 'Sin Filtro'),
        ('antireflejo', 'Antireflejo'),
        ('luz_azul', 'Filtro Luz Azul'),
        ('fotocromatico', 'Fotocromático'),
        ('polarizado', 'Polarizado'),
        ('uv', 'Filtro UV'),
    ]
    
    paciente = models.ForeignKey(
        Paciente,
        verbose_name=_('paciente'),
        on_delete=models.CASCADE,
        related_name='diagnosticos'
    )
    
    # Datos clínicos en formato JSON para máxima flexibilidad
    datos_clinicos = models.JSONField(
        _('datos clínicos'),
        default=dict,
        blank=True,
        help_text=_('Datos clínicos del diagnóstico en formato JSON')
    )
    
    tipo_lente = models.CharField(
        _('tipo de lente'),
        max_length=20,
        choices=TIPO_LENTE_CHOICES,
        blank=True
    )
    material_lente = models.CharField(
        _('material del lente'),
        max_length=20,
        choices=MATERIAL_LENTE_CHOICES,
        blank=True
    )
    filtro_lente = models.CharField(
        _('filtro del lente'),
        max_length=20,
        choices=FILTRO_LENTE_CHOICES,
        default='ninguno'
    )
    
    proximo_control = models.DateField(_('próximo control'), null=True, blank=True)
    recordatorio_enviado = models.BooleanField(_('recordatorio enviado'), default=False)
    remision_oftalmologica = models.BooleanField(_('remisión oftalmológica'), default=False)
    observaciones_adicionales = models.TextField(_('observaciones adicionales'), blank=True)
    
    comentario = models.TextField(_('comentario'), blank=True)
    fecha_hora_consulta = models.DateTimeField(_('fecha y hora de la consulta'))
    usuario_creacion = models.ForeignKey(
        Usuario,
        verbose_name=_('usuario de creación'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='diagnosticos_creados'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name=_('sucursal'),
        on_delete=models.CASCADE,
        related_name='diagnosticos'
    )
    activo = models.BooleanField(_('activo'), default=True)
    creado_en = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    actualizado_en = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('diagnóstico')
        verbose_name_plural = _('diagnósticos')
        ordering = ['-fecha_hora_consulta']
        indexes = [
            models.Index(fields=['fecha_hora_consulta']),
            models.Index(fields=['paciente', 'fecha_hora_consulta']),
            models.Index(fields=['proximo_control']),
        ]

    def __str__(self):
        return f"Diagnóstico - {self.paciente.nombre_completo} - {self.fecha_hora_consulta.strftime('%d/%m/%Y %H:%M')}"

    @property
    def necesita_recordatorio(self):
        """Verifica si necesita enviar recordatorio para próximo control"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.proximo_control or self.recordatorio_enviado:
            return False
        
        # Enviar recordatorio 7 días antes de la fecha del próximo control
        fecha_recordatorio = self.proximo_control - timedelta(days=7)
        return timezone.now().date() >= fecha_recordatorio

    @property
    def dias_hasta_proximo_control(self):
        """Calcula los días hasta el próximo control"""
        if not self.proximo_control:
            return None
        
        from django.utils import timezone
        diferencia = self.proximo_control - timezone.now().date()
        return diferencia.days

    def get_dato_clinico(self, campo, default=''):
        """Obtiene un dato clínico específico del JSON"""
        return self.datos_clinicos.get(campo, default)

    def set_dato_clinico(self, campo, valor):
        """Establece un dato clínico específico en el JSON"""
        if not self.datos_clinicos:
            self.datos_clinicos = {}
        self.datos_clinicos[campo] = valor

    @property
    def rx_en_uso(self):
        return self.get_dato_clinico('rx_en_uso')

    @property
    def antecedentes_medicos(self):
        return self.get_dato_clinico('antecedentes_medicos')

    @property
    def sintomas_signos(self):
        return self.get_dato_clinico('sintomas_signos')

    @property
    def analisis_panoramico(self):
        return self.get_dato_clinico('analisis_panoramico')

    @property
    def examen_ojo_derecho(self):
        return self.get_dato_clinico('examen_ojo_derecho')

    @property
    def examen_ojo_izquierdo(self):
        return self.get_dato_clinico('examen_ojo_izquierdo')

    @property
    def analisis_pantoscopico(self):
        return self.get_dato_clinico('analisis_pantoscopico')

    @property
    def analisis_vertice(self):
        return self.get_dato_clinico('analisis_vertice')

    @property
    def anamnesis_paciente(self):
        return self.get_dato_clinico('anamnesis_paciente')

    @property
    def hallazgos_encontrados(self):
        return self.get_dato_clinico('hallazgos_encontrados')

    @property
    def diagnostico_tratamiento(self):
        return self.get_dato_clinico('diagnostico_tratamiento')

    @property
    def retinoscopia(self):
        return self.get_dato_clinico('retinoscopia')

    @property
    def agudeza_visual(self):
        return self.get_dato_clinico('agudeza_visual')

    @property
    def afinacion_subjetiva(self):
        return self.get_dato_clinico('afinacion_subjetiva')

    @property
    def rx_final(self):
        return self.get_dato_clinico('rx_final')

    @classmethod
    def get_campos_clinicos_disponibles(cls):
        """Retorna la lista de campos clínicos disponibles"""
        return [
            'rx_en_uso',
            'antecedentes_medicos', 
            'sintomas_signos',
            'analisis_panoramico',
            'examen_ojo_derecho',
            'examen_ojo_izquierdo',
            'analisis_pantoscopico',
            'analisis_vertice',
            'anamnesis_paciente',
            'hallazgos_encontrados',
            'diagnostico_tratamiento',
            'retinoscopia',
            'agudeza_visual',
            'afinacion_subjetiva',
            'rx_final'
        ]

    def get_estructura_datos_clinicos(self):
        """Retorna la estructura completa de datos clínicos"""
        estructura = {}
        for campo in self.get_campos_clinicos_disponibles():
            estructura[campo] = self.get_dato_clinico(campo)
        return estructura

# Create your models here.

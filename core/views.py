from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Paciente, CitaMedica, Diagnostico
from .serializers import (
    PacienteSerializer,
    PacienteCreateSerializer,
    PacienteListSerializer,
    CitaMedicaSerializer,
    CitaMedicaCreateSerializer,
    CitaMedicaListSerializer,
    CitaMedicaCambioEstadoSerializer,
    DiagnosticoSerializer,
    DiagnosticoCreateSerializer,
    DiagnosticoListSerializer,
    DiagnosticoResumenSerializer,
    RecordatorioSerializer
)

def format_error_response(errors):
    """Formatea los errores del serializer en un formato más amigable"""
    if isinstance(errors, dict):
        error_messages = []
        for field, field_errors in errors.items():
            if isinstance(field_errors, list):
                for error in field_errors:
                    error_messages.append(f"{field}: {error}")
            else:
                error_messages.append(f"{field}: {field_errors}")
        return {"error": " ".join(error_messages)}
    return {"error": str(errors)}

# Vistas de Pacientes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_pacientes(request):
    """Lista todos los pacientes con paginación y filtros de búsqueda"""
    queryset = Paciente.objects.select_related('usuario_registro', 'sucursal').filter(activo=True)
    
    # Filtros de búsqueda
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(nombre_completo__icontains=search) |
            Q(codigo_paciente__icontains=search) |
            Q(correo__icontains=search) |
            Q(telefono__icontains=search)
        )
    
    # Filtro por sucursal
    sucursal_id = request.query_params.get('sucursal', None)
    if sucursal_id:
        queryset = queryset.filter(sucursal_id=sucursal_id)
    
    # Filtro por género
    genero = request.query_params.get('genero', None)
    if genero:
        queryset = queryset.filter(genero=genero)
    
    # Paginación
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)
    
    try:
        page_size = int(page_size)
        if page_size > 100:  # Límite máximo
            page_size = 100
    except ValueError:
        page_size = 10
    
    paginator = Paginator(queryset, page_size)
    
    try:
        pacientes = paginator.page(page)
    except PageNotAnInteger:
        pacientes = paginator.page(1)
    except EmptyPage:
        pacientes = paginator.page(paginator.num_pages)
    
    serializer = PacienteListSerializer(pacientes, many=True)
    
    return Response({
        'results': serializer.data,
        'pagination': {
            'current_page': pacientes.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': pacientes.has_next(),
            'has_previous': pacientes.has_previous(),
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_paciente(request):
    """Crea un nuevo paciente"""
    serializer = PacienteCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        paciente = serializer.save()
        # Retornar el paciente creado con todos los datos
        response_serializer = PacienteSerializer(paciente)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_paciente(request, pk):
    """Obtiene un paciente específico por ID"""
    try:
        paciente = Paciente.objects.select_related('usuario_registro', 'sucursal').get(pk=pk, activo=True)
        serializer = PacienteSerializer(paciente)
        return Response(serializer.data)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_paciente(request, pk):
    """Actualiza un paciente existente"""
    try:
        paciente = Paciente.objects.get(pk=pk, activo=True)
        serializer = PacienteSerializer(paciente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_paciente(request, pk):
    """Elimina un paciente (cambio de estado a inactivo)"""
    try:
        paciente = Paciente.objects.get(pk=pk, activo=True)
        paciente.activo = False
        paciente.save()
        return Response({"mensaje": "Paciente desactivado correctamente"}, status=status.HTTP_200_OK)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activar_paciente(request, pk):
    """Activa un paciente (cambio de estado a activo)"""
    try:
        paciente = Paciente.objects.get(pk=pk, activo=False)
        paciente.activo = True
        paciente.save()
        return Response({"mensaje": "Paciente activado correctamente"}, status=status.HTTP_200_OK)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_paciente_por_codigo(request, codigo):
    """Busca un paciente por su código"""
    try:
        paciente = Paciente.objects.select_related('usuario_registro', 'sucursal').get(
            codigo_paciente=codigo, activo=True
        )
        serializer = PacienteSerializer(paciente)
        return Response(serializer.data)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=status.HTTP_404_NOT_FOUND)


# Vistas de Citas Médicas
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas(request):
    """Lista todas las citas médicas con paginación y filtros"""
    queryset = CitaMedica.objects.select_related(
        'paciente', 'doctor_asignado', 'usuario_creacion', 'sucursal'
    ).filter(activo=True)
    
    # Filtros de búsqueda
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(paciente__nombre_completo__icontains=search) |
            Q(paciente__codigo_paciente__icontains=search) |
            Q(doctor_asignado__nombre_completo__icontains=search)
        )
    
    # Filtro por estado
    estado = request.query_params.get('estado', None)
    if estado:
        queryset = queryset.filter(estado=estado)
    
    # Filtro por sucursal
    sucursal_id = request.query_params.get('sucursal', None)
    if sucursal_id:
        queryset = queryset.filter(sucursal_id=sucursal_id)
    
    # Filtro por doctor
    doctor_id = request.query_params.get('doctor', None)
    if doctor_id:
        queryset = queryset.filter(doctor_asignado_id=doctor_id)
    
    # Filtro por paciente
    paciente_id = request.query_params.get('paciente', None)
    if paciente_id:
        queryset = queryset.filter(paciente_id=paciente_id)
    
    # Filtro por fecha
    fecha_desde = request.query_params.get('fecha_desde', None)
    fecha_hasta = request.query_params.get('fecha_hasta', None)
    if fecha_desde:
        queryset = queryset.filter(fecha_hora__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(fecha_hora__lte=fecha_hasta)
    
    # Paginación
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)
    
    try:
        page_size = int(page_size)
        if page_size > 100:  # Límite máximo
            page_size = 100
    except ValueError:
        page_size = 10
    
    paginator = Paginator(queryset, page_size)
    
    try:
        citas = paginator.page(page)
    except PageNotAnInteger:
        citas = paginator.page(1)
    except EmptyPage:
        citas = paginator.page(paginator.num_pages)
    
    serializer = CitaMedicaListSerializer(citas, many=True)
    
    return Response({
        'results': serializer.data,
        'pagination': {
            'current_page': citas.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': citas.has_next(),
            'has_previous': citas.has_previous(),
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_cita(request):
    """Crea una nueva cita médica"""
    serializer = CitaMedicaCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        cita = serializer.save()
        # Retornar la cita creada con todos los datos
        response_serializer = CitaMedicaSerializer(cita)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_cita(request, pk):
    """Obtiene una cita médica específica por ID"""
    try:
        cita = CitaMedica.objects.select_related(
            'paciente', 'doctor_asignado', 'usuario_creacion', 'sucursal'
        ).get(pk=pk, activo=True)
        serializer = CitaMedicaSerializer(cita)
        return Response(serializer.data)
    except CitaMedica.DoesNotExist:
        return Response({"error": "Cita médica no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_cita(request, pk):
    """Actualiza una cita médica existente"""
    try:
        cita = CitaMedica.objects.get(pk=pk, activo=True)
        serializer = CitaMedicaSerializer(cita, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    except CitaMedica.DoesNotExist:
        return Response({"error": "Cita médica no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_cita(request, pk):
    """Elimina una cita médica (cambio de estado a inactivo)"""
    try:
        cita = CitaMedica.objects.get(pk=pk, activo=True)
        cita.activo = False
        cita.save()
        return Response({"mensaje": "Cita médica eliminada correctamente"}, status=status.HTTP_200_OK)
    except CitaMedica.DoesNotExist:
        return Response({"error": "Cita médica no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_estado_cita(request, pk):
    """Cambia el estado de una cita médica"""
    try:
        cita = CitaMedica.objects.get(pk=pk, activo=True)
        serializer = CitaMedicaCambioEstadoSerializer(data=request.data)
        
        if serializer.is_valid():
            nuevo_estado = serializer.validated_data['nuevo_estado']
            
            # Validar transiciones de estado
            if nuevo_estado == 'confirmada' and not cita.puede_confirmar:
                return Response(
                    {"error": "No se puede confirmar esta cita en su estado actual"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif nuevo_estado == 'reagendada' and not cita.puede_reagendar:
                return Response(
                    {"error": "No se puede reagendar esta cita en su estado actual"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif nuevo_estado == 'cancelada' and not cita.puede_cancelar:
                return Response(
                    {"error": "No se puede cancelar esta cita en su estado actual"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif nuevo_estado == 'en_progreso' and not cita.puede_iniciar:
                return Response(
                    {"error": "No se puede iniciar esta cita en su estado actual"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif nuevo_estado == 'finalizada' and not cita.puede_finalizar:
                return Response(
                    {"error": "No se puede finalizar esta cita en su estado actual"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Aplicar cambios
            cita.estado = nuevo_estado
            
            if serializer.validated_data.get('comentarios'):
                cita.comentarios = serializer.validated_data['comentarios']
            
            if serializer.validated_data.get('nueva_fecha_hora'):
                cita.fecha_hora = serializer.validated_data['nueva_fecha_hora']
            
            if serializer.validated_data.get('nuevo_doctor'):
                cita.doctor_asignado = serializer.validated_data['nuevo_doctor']
            
            cita.save()
            
            # Retornar cita actualizada
            response_serializer = CitaMedicaSerializer(cita)
            return Response(response_serializer.data)
        
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    
    except CitaMedica.DoesNotExist:
        return Response({"error": "Cita médica no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reasignar_doctor(request, pk):
    """Reasigna el doctor de una cita médica"""
    try:
        cita = CitaMedica.objects.get(pk=pk, activo=True)
        nuevo_doctor_id = request.data.get('doctor_id')
        
        if not nuevo_doctor_id:
            return Response(
                {"error": "Se requiere el ID del nuevo doctor"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            Usuario = get_user_model()
            nuevo_doctor = Usuario.objects.get(id=nuevo_doctor_id, is_active=True)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Doctor no encontrado o inactivo"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        cita.doctor_asignado = nuevo_doctor
        cita.save()
        
        serializer = CitaMedicaSerializer(cita)
        return Response(serializer.data)
    
    except CitaMedica.DoesNotExist:
        return Response({"error": "Cita médica no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def citas_por_doctor(request, doctor_id):
    """Lista las citas asignadas a un doctor específico"""
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    try:
        doctor = Usuario.objects.get(id=doctor_id, is_active=True)
    except Usuario.DoesNotExist:
        return Response({"error": "Doctor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    queryset = CitaMedica.objects.select_related(
        'paciente', 'usuario_creacion', 'sucursal'
    ).filter(doctor_asignado=doctor, activo=True)
    
    # Filtro por fecha
    fecha_desde = request.query_params.get('fecha_desde', None)
    fecha_hasta = request.query_params.get('fecha_hasta', None)
    if fecha_desde:
        queryset = queryset.filter(fecha_hora__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(fecha_hora__lte=fecha_hasta)
    
    # Filtro por estado
    estado = request.query_params.get('estado', None)
    if estado:
        queryset = queryset.filter(estado=estado)
    
    serializer = CitaMedicaListSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def citas_por_paciente(request, paciente_id):
    """Lista las citas de un paciente específico"""
    try:
        paciente = Paciente.objects.get(id=paciente_id, activo=True)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    queryset = CitaMedica.objects.select_related(
        'doctor_asignado', 'usuario_creacion', 'sucursal'
    ).filter(paciente=paciente, activo=True)
    
    serializer = CitaMedicaListSerializer(queryset, many=True)
    return Response(serializer.data)


# Vistas de Diagnósticos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_diagnosticos(request):
    """Lista todos los diagnósticos con paginación y filtros"""
    queryset = Diagnostico.objects.select_related(
        'paciente', 'usuario_creacion', 'sucursal'
    ).filter(activo=True)
    
    # Filtros de búsqueda
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(paciente__nombre_completo__icontains=search) |
            Q(paciente__codigo_paciente__icontains=search) |
            Q(datos_clinicos__rx_final__icontains=search) |
            Q(datos_clinicos__diagnostico_tratamiento__icontains=search) |
            Q(datos_clinicos__hallazgos_encontrados__icontains=search) |
            Q(comentario__icontains=search)
        )
    
    # Filtro por sucursal
    sucursal_id = request.query_params.get('sucursal', None)
    if sucursal_id:
        queryset = queryset.filter(sucursal_id=sucursal_id)
    
    # Filtro por paciente
    paciente_id = request.query_params.get('paciente', None)
    if paciente_id:
        queryset = queryset.filter(paciente_id=paciente_id)
    
    # Filtro por tipo de lente
    tipo_lente = request.query_params.get('tipo_lente', None)
    if tipo_lente:
        queryset = queryset.filter(tipo_lente=tipo_lente)
    
    # Filtro por remisión oftalmológica
    remision = request.query_params.get('remision_oftalmologica', None)
    if remision:
        queryset = queryset.filter(remision_oftalmologica=remision.lower() == 'true')
    
    # Filtro por fecha de consulta
    fecha_desde = request.query_params.get('fecha_desde', None)
    fecha_hasta = request.query_params.get('fecha_hasta', None)
    if fecha_desde:
        queryset = queryset.filter(fecha_hora_consulta__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(fecha_hora_consulta__lte=fecha_hasta)
    
    # Filtro por próximos controles
    proximos_controles = request.query_params.get('proximos_controles', None)
    if proximos_controles:
        from django.utils import timezone
        from datetime import timedelta
        fecha_limite = timezone.now().date() + timedelta(days=30)
        queryset = queryset.filter(
            proximo_control__lte=fecha_limite,
            proximo_control__gte=timezone.now().date()
        )
    
    # Paginación
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)
    
    try:
        page_size = int(page_size)
        if page_size > 100:  # Límite máximo
            page_size = 100
    except ValueError:
        page_size = 10
    
    paginator = Paginator(queryset, page_size)
    
    try:
        diagnosticos = paginator.page(page)
    except PageNotAnInteger:
        diagnosticos = paginator.page(1)
    except EmptyPage:
        diagnosticos = paginator.page(paginator.num_pages)
    
    serializer = DiagnosticoListSerializer(diagnosticos, many=True)
    
    return Response({
        'results': serializer.data,
        'pagination': {
            'current_page': diagnosticos.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': diagnosticos.has_next(),
            'has_previous': diagnosticos.has_previous(),
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_diagnostico(request):
    """Crea un nuevo diagnóstico"""
    serializer = DiagnosticoCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        diagnostico = serializer.save()
        # Retornar el diagnóstico creado con todos los datos
        response_serializer = DiagnosticoSerializer(diagnostico)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_diagnostico(request, pk):
    """Obtiene un diagnóstico específico por ID"""
    try:
        diagnostico = Diagnostico.objects.select_related(
            'paciente', 'usuario_creacion', 'sucursal'
        ).get(pk=pk, activo=True)
        serializer = DiagnosticoSerializer(diagnostico)
        return Response(serializer.data)
    except Diagnostico.DoesNotExist:
        return Response({"error": "Diagnóstico no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_diagnostico(request, pk):
    """Actualiza un diagnóstico existente"""
    try:
        diagnostico = Diagnostico.objects.get(pk=pk, activo=True)
        serializer = DiagnosticoSerializer(diagnostico, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    except Diagnostico.DoesNotExist:
        return Response({"error": "Diagnóstico no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_diagnostico(request, pk):
    """Elimina un diagnóstico (cambio de estado a inactivo)"""
    try:
        diagnostico = Diagnostico.objects.get(pk=pk, activo=True)
        diagnostico.activo = False
        diagnostico.save()
        return Response({"mensaje": "Diagnóstico eliminado correctamente"}, status=status.HTTP_200_OK)
    except Diagnostico.DoesNotExist:
        return Response({"error": "Diagnóstico no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def diagnosticos_por_paciente(request, paciente_id):
    """Lista los diagnósticos de un paciente específico"""
    try:
        paciente = Paciente.objects.get(id=paciente_id, activo=True)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    queryset = Diagnostico.objects.select_related(
        'usuario_creacion', 'sucursal'
    ).filter(paciente=paciente, activo=True)
    
    serializer = DiagnosticoResumenSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recordatorios_pendientes(request):
    """Lista los pacientes que necesitan recordatorio para próximo control"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Obtener diagnósticos que necesitan recordatorio (próximos 7 días)
    fecha_limite = timezone.now().date() + timedelta(days=7)
    
    queryset = Diagnostico.objects.select_related('paciente').filter(
        proximo_control__lte=fecha_limite,
        proximo_control__gte=timezone.now().date(),
        recordatorio_enviado=False,
        activo=True
    )
    
    recordatorios = []
    for diagnostico in queryset:
        recordatorios.append({
            'diagnostico_id': diagnostico.id,
            'paciente_nombre': diagnostico.paciente.nombre_completo,
            'proximo_control': diagnostico.proximo_control,
            'dias_restantes': diagnostico.dias_hasta_proximo_control,
            'contacto_paciente': diagnostico.paciente.telefono or diagnostico.paciente.correo
        })
    
    serializer = RecordatorioSerializer(recordatorios, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_recordatorio_enviado(request, pk):
    """Marca un recordatorio como enviado"""
    try:
        diagnostico = Diagnostico.objects.get(pk=pk, activo=True)
        diagnostico.recordatorio_enviado = True
        diagnostico.save()
        return Response({"mensaje": "Recordatorio marcado como enviado"}, status=status.HTTP_200_OK)
    except Diagnostico.DoesNotExist:
        return Response({"error": "Diagnóstico no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_diagnosticos(request):
    """Obtiene estadísticas de diagnósticos"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Estadísticas generales
    total_diagnosticos = Diagnostico.objects.filter(activo=True).count()
    diagnosticos_este_mes = Diagnostico.objects.filter(
        activo=True,
        creado_en__month=timezone.now().month,
        creado_en__year=timezone.now().year
    ).count()
    
    # Próximos controles (próximos 30 días)
    fecha_limite = timezone.now().date() + timedelta(days=30)
    proximos_controles = Diagnostico.objects.filter(
        proximo_control__lte=fecha_limite,
        proximo_control__gte=timezone.now().date(),
        activo=True
    ).count()
    
    # Recordatorios pendientes
    recordatorios_pendientes = Diagnostico.objects.filter(
        proximo_control__lte=timezone.now().date() + timedelta(days=7),
        proximo_control__gte=timezone.now().date(),
        recordatorio_enviado=False,
        activo=True
    ).count()
    
    # Tipos de lentes más comunes
    tipos_lentes = Diagnostico.objects.filter(activo=True).exclude(tipo_lente='').values('tipo_lente').annotate(
        count=Count('tipo_lente')
    ).order_by('-count')[:5]
    
    # Remisiones oftalmológicas
    remisiones_oftalmologicas = Diagnostico.objects.filter(
        activo=True,
        remision_oftalmologica=True
    ).count()
    
    return Response({
        'total_diagnosticos': total_diagnosticos,
        'diagnosticos_este_mes': diagnosticos_este_mes,
        'proximos_controles': proximos_controles,
        'recordatorios_pendientes': recordatorios_pendientes,
        'tipos_lentes_mas_comunes': tipos_lentes,
        'remisiones_oftalmologicas': remisiones_oftalmologicas
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estructura_datos_clinicos(request):
    """Obtiene la estructura de campos clínicos disponibles"""
    estructura = {
        'campos_disponibles': Diagnostico.get_campos_clinicos_disponibles(),
        'ejemplo_estructura': {
            'rx_en_uso': 'OD: +2.00 -0.50 x 90°, OI: +1.75 -0.25 x 85°',
            'antecedentes_medicos': 'Diabetes tipo 2, hipertensión arterial',
            'sintomas_signos': 'Visión borrosa de cerca, fatiga visual',
            'analisis_panoramico': 'Córneas transparentes, pupilas reactivas',
            'examen_ojo_derecho': 'AV: 20/40, refracción: +2.25 -0.75 x 90°',
            'examen_ojo_izquierdo': 'AV: 20/30, refracción: +2.00 -0.50 x 85°',
            'analisis_pantoscopico': 'Ángulo pantoscópico: 12°',
            'analisis_vertice': 'Distancia al vértice: 12mm',
            'anamnesis_paciente': 'Trabajo prolongado en computadora, 8 horas diarias',
            'hallazgos_encontrados': 'Presbicia progresiva, astigmatismo leve bilateral',
            'diagnostico_tratamiento': 'Lentes progresivos con filtro luz azul',
            'retinoscopia': 'OD: +2.25 -0.75 x 90°, OI: +2.00 -0.50 x 85°',
            'agudeza_visual': 'SC: OD 20/40, OI 20/30. CC: OD 20/25, OI 20/20',
            'afinacion_subjetiva': 'Se confirma Rx objetiva, tolera bien la adición',
            'rx_final': 'OD: +2.25 -0.75 x 90° ADD +1.50, OI: +2.00 -0.50 x 85° ADD +1.50'
        },
        'tipos_lente_disponibles': [choice[0] for choice in Diagnostico.TIPO_LENTE_CHOICES],
        'materiales_lente_disponibles': [choice[0] for choice in Diagnostico.MATERIAL_LENTE_CHOICES],
        'filtros_lente_disponibles': [choice[0] for choice in Diagnostico.FILTRO_LENTE_CHOICES],
        'descripcion': 'Estructura flexible para datos clínicos. Puedes enviar campos individuales o el objeto JSON completo.'
    }
    
    return Response(estructura)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validar_estructura_datos_clinicos(request):
    """Valida una estructura de datos clínicos antes de crear el diagnóstico"""
    datos_clinicos = request.data.get('datos_clinicos', {})
    
    if not isinstance(datos_clinicos, dict):
        return Response(
            {"error": "Los datos clínicos deben ser un objeto JSON"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    campos_validos = Diagnostico.get_campos_clinicos_disponibles()
    campos_invalidos = []
    
    for campo in datos_clinicos.keys():
        if campo not in campos_validos:
            campos_invalidos.append(campo)
    
    if campos_invalidos:
        return Response({
            "warning": f"Los siguientes campos no son reconocidos: {', '.join(campos_invalidos)}",
            "campos_validos": campos_validos,
            "estructura_recibida": datos_clinicos
        })
    
    return Response({
        "mensaje": "Estructura válida",
        "campos_recibidos": list(datos_clinicos.keys()),
        "estructura_recibida": datos_clinicos
    })

# Create your views here.

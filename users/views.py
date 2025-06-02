from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Permiso, Rol, Sucursal
from .serializers import (
    PermisoSerializer,
    RolSerializer,
    SucursalSerializer,
    SucursalCreateSerializer,
    UsuarioSerializer,
    UsuarioCreateSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny

Usuario = get_user_model()

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

# Vistas de Permisos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_permisos(request):
    queryset = Permiso.objects.all()
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(nombre__icontains=search) |
            Q(codigo__icontains=search)
        )
    serializer = PermisoSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_permiso(request):
    serializer = PermisoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_permiso(request, pk):
    try:
        permiso = Permiso.objects.get(pk=pk)
        serializer = PermisoSerializer(permiso)
        return Response(serializer.data)
    except Permiso.DoesNotExist:
        return Response({"error": "Permiso no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_permiso(request, pk):
    try:
        permiso = Permiso.objects.get(pk=pk)
        serializer = PermisoSerializer(permiso, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    except Permiso.DoesNotExist:
        return Response({"error": "Permiso no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_permiso(request, pk):
    try:
        permiso = Permiso.objects.get(pk=pk)
        permiso.activo = False
        permiso.save()
        return Response({"mensaje": "Permiso desactivado correctamente"}, status=status.HTTP_200_OK)
    except Permiso.DoesNotExist:
        return Response({"error": "Permiso no encontrado"}, status=status.HTTP_404_NOT_FOUND)

# Vistas de Roles
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_roles(request):
    queryset = Rol.objects.all()
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(nombre__icontains=search)
    serializer = RolSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_rol(request):
    serializer = RolSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_rol(request, pk):
    try:
        rol = Rol.objects.get(pk=pk)
        serializer = RolSerializer(rol)
        return Response(serializer.data)
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_rol(request, pk):
    try:
        rol = Rol.objects.get(pk=pk)
        serializer = RolSerializer(rol, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_rol(request, pk):
    try:
        rol = Rol.objects.get(pk=pk)
        rol.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asignar_permisos_rol(request, pk):
    try:
        rol = Rol.objects.get(pk=pk)
        permisos_ids = request.data.get('permisos', [])
        
        permisos = []
        for permiso_id in permisos_ids:
            try:
                permiso = Permiso.objects.get(id=permiso_id)
                permisos.append(permiso)
            except Permiso.DoesNotExist:
                return Response(
                    {"error": f"El permiso con ID {permiso_id} no existe"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            rol.permisos.clear()
            for permiso in permisos:
                rol.permisos.add(permiso)
            
            rol.refresh_from_db()
            serializer = RolSerializer(rol)
            return Response(serializer.data)
            
        except Exception as e:
            rol.refresh_from_db()
            return Response(
                {"error": f"Error al asignar los permisos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

# Vistas de Sucursales
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_sucursales(request):
    queryset = Sucursal.objects.all()
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(nombre__icontains=search) |
            Q(direccion__icontains=search)
        )
    serializer = SucursalSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_sucursal(request):
    serializer = SucursalCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_sucursal(request, pk):
    try:
        sucursal = Sucursal.objects.get(pk=pk)
        serializer = SucursalSerializer(sucursal)
        return Response(serializer.data)
    except Sucursal.DoesNotExist:
        return Response({"error": "Sucursal no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_sucursal(request, pk):
    try:
        sucursal = Sucursal.objects.get(pk=pk)
        serializer = SucursalSerializer(sucursal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    except Sucursal.DoesNotExist:
        return Response({"error": "Sucursal no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_sucursal(request, pk):
    try:
        sucursal = Sucursal.objects.get(pk=pk)
        sucursal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Sucursal.DoesNotExist:
        return Response({"error": "Sucursal no encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_estado_sucursal(request, pk):
    try:
        sucursal = Sucursal.objects.get(pk=pk)
        activo = request.data.get('activo')
        if activo is None:
            return Response({"error": "El campo 'activo' es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        sucursal.activo = activo
        sucursal.save()
        serializer = SucursalSerializer(sucursal)
        return Response(serializer.data)
    except Sucursal.DoesNotExist:
        return Response({"error": "Sucursal no encontrada"}, status=status.HTTP_404_NOT_FOUND)

# Vistas de Usuarios
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_usuarios(request):
    queryset = Usuario.objects.all()
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(username__icontains=search) |
            Q(nombre_completo__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Obtener todos los roles y sucursales
    roles = Rol.objects.all()
    sucursales = Sucursal.objects.all()
    
    # Serializar usuarios, roles y sucursales
    usuarios_serializer = UsuarioSerializer(queryset, many=True)
    roles_serializer = RolSerializer(roles, many=True)
    sucursales_serializer = SucursalSerializer(sucursales, many=True)
    
    return Response({
        'usuarios': usuarios_serializer.data,
        'roles': roles_serializer.data,
        'sucursales': sucursales_serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_usuario(request):
    serializer = UsuarioCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_usuario(request, pk):
    try:
        usuario = Usuario.objects.get(pk=pk)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_usuario(request, pk):
    try:
        usuario = Usuario.objects.get(pk=pk)
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(format_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_usuario(request, pk):
    try:
        usuario = Usuario.objects.get(pk=pk)
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_perfil(request):
    # Obtener todos los roles y sucursales
    roles = Rol.objects.all()
    sucursales = Sucursal.objects.all()
    
    # Serializar usuario, roles y sucursales
    usuario_serializer = UsuarioSerializer(request.user)
    roles_serializer = RolSerializer(roles, many=True)
    sucursales_serializer = SucursalSerializer(sucursales, many=True)
    
    return Response({
        'usuario': usuario_serializer.data,
        'roles': roles_serializer.data,
        'sucursales': sucursales_serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_password(request):
    usuario = request.user
    password_actual = request.data.get('password_actual')
    password_nuevo = request.data.get('password_nuevo')
    confirmar_password = request.data.get('confirmar_password')

    if not password_actual or not password_nuevo or not confirmar_password:
        return Response(
            {"error": "Todos los campos son requeridos"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not usuario.check_password(password_actual):
        return Response(
            {"error": "La contraseña actual es incorrecta"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if password_nuevo != confirmar_password:
        return Response(
            {"error": "Las contraseñas no coinciden"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password_nuevo) < 8:
        return Response(
            {"error": "La contraseña debe tener al menos 8 caracteres"},
            status=status.HTTP_400_BAD_REQUEST
        )

    usuario.set_password(password_nuevo)
    usuario.save()
    return Response({"message": "Contraseña actualizada correctamente"})

# Vista de Autenticación
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response 
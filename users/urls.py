from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # Vistas de Permisos
    listar_permisos,
    crear_permiso,
    obtener_permiso,
    actualizar_permiso,
    eliminar_permiso,
    
    # Vistas de Roles
    listar_roles,
    crear_rol,
    obtener_rol,
    actualizar_rol,
    eliminar_rol,
    asignar_permisos_rol,
    
    # Vistas de Sucursales
    listar_sucursales,
    crear_sucursal,
    obtener_sucursal,
    actualizar_sucursal,
    eliminar_sucursal,
    cambiar_estado_sucursal,
    
    # Vistas de Usuarios
    listar_usuarios,
    crear_usuario,
    obtener_usuario,
    actualizar_usuario,
    eliminar_usuario,
    obtener_perfil,
    cambiar_password,
    
    # Vistas de Autenticación
    CustomTokenObtainPairView,
)

app_name = 'users'

urlpatterns = [
    # Rutas de autenticación
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rutas de permisos
    path('permisos/', listar_permisos, name='permiso-list'),
    path('permisos/crear/', crear_permiso, name='permiso-create'),
    path('permisos/<int:pk>/', obtener_permiso, name='permiso-detail'),
    path('permisos/<int:pk>/actualizar/', actualizar_permiso, name='permiso-update'),
    path('permisos/<int:pk>/eliminar/', eliminar_permiso, name='permiso-delete'),
    
    # Rutas de roles
    path('roles/', listar_roles, name='rol-list'),
    path('roles/crear/', crear_rol, name='rol-create'),
    path('roles/<int:pk>/', obtener_rol, name='rol-detail'),
    path('roles/<int:pk>/actualizar/', actualizar_rol, name='rol-update'),
    path('roles/<int:pk>/eliminar/', eliminar_rol, name='rol-delete'),
    path('roles/<int:pk>/asignar-permisos/', asignar_permisos_rol, name='rol-asignar-permisos'),
    
    # Rutas de sucursales
    path('sucursales/', listar_sucursales, name='sucursal-list'),
    path('sucursales/crear/', crear_sucursal, name='sucursal-create'),
    path('sucursales/<int:pk>/', obtener_sucursal, name='sucursal-detail'),
    path('sucursales/<int:pk>/actualizar/', actualizar_sucursal, name='sucursal-update'),
    path('sucursales/<int:pk>/eliminar/', eliminar_sucursal, name='sucursal-delete'),
    path('sucursales/<int:pk>/cambiar-estado/', cambiar_estado_sucursal, name='sucursal-cambiar-estado'),
    
    # Rutas de usuarios
    path('usuarios/', listar_usuarios, name='usuario-list'),
    path('usuarios/crear/', crear_usuario, name='usuario-create'),
    path('usuarios/<int:pk>/', obtener_usuario, name='usuario-detail'),
    path('usuarios/<int:pk>/actualizar/', actualizar_usuario, name='usuario-update'),
    path('usuarios/<int:pk>/eliminar/', eliminar_usuario, name='usuario-delete'),
    path('usuarios/perfil/', obtener_perfil, name='usuario-perfil'),
    path('usuarios/cambiar-password/', cambiar_password, name='usuario-cambiar-password'),
] 
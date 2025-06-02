from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Permiso, Rol, Sucursal

Usuario = get_user_model()

class UsuarioTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Crear un rol de prueba
        self.rol = Rol.objects.create(nombre='Administrador')
        # Crear un permiso de prueba
        self.permiso = Permiso.objects.create(
            nombre='Gestionar Usuarios',
            codigo='gestionar_usuarios'
        )
        self.rol.permisos.add(self.permiso)
        # Crear un usuario de prueba
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            nombre_completo='Usuario de Prueba',
            rol=self.rol
        )
        # Obtener token de autenticación
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_obtener_perfil(self):
        """Test para obtener el perfil del usuario autenticado"""
        response = self.client.get('/api/users/perfil/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_cambiar_password(self):
        """Test para cambiar la contraseña del usuario"""
        response = self.client.post('/api/users/cambiar-password/', {
            'password_actual': 'testpass123',
            'password_nuevo': 'newpass123',
            'confirmar_password': 'newpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Contraseña actualizada correctamente')

    def test_crear_usuario(self):
        """Test para crear un nuevo usuario"""
        data = {
            'username': 'nuevousuario',
            'password': 'nuevopass123',
            'email': 'nuevo@example.com',
            'nombre_completo': 'Nuevo Usuario',
            'rol': self.rol.id
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 2)

class RolTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rol = Rol.objects.create(nombre='Administrador')
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            nombre_completo='Usuario de Prueba',
            rol=self.rol
        )
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_listar_roles(self):
        """Test para listar roles"""
        response = self.client.get('/api/roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_crear_rol(self):
        """Test para crear un nuevo rol"""
        data = {
            'nombre': 'Nuevo Rol'
        }
        response = self.client.post('/api/roles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rol.objects.count(), 2)

class PermisoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rol = Rol.objects.create(nombre='Administrador')
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            nombre_completo='Usuario de Prueba',
            rol=self.rol
        )
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_crear_permiso(self):
        """Test para crear un nuevo permiso"""
        data = {
            'nombre': 'Nuevo Permiso',
            'codigo': 'nuevo_permiso'
        }
        response = self.client.post('/api/permisos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Permiso.objects.count(), 1)

    def test_asignar_permisos_rol(self):
        """Test para asignar permisos a un rol"""
        permiso = Permiso.objects.create(
            nombre='Test Permiso',
            codigo='test_permiso'
        )
        data = {
            'permisos': [permiso.id]
        }
        response = self.client.post(
            f'/api/roles/{self.rol.id}/asignar-permisos/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.rol.permisos.count(), 1)

    def test_permiso_genera_codigo_automaticamente(self):
        """Test para verificar que el permiso genera el código automáticamente"""
        permiso = Permiso.objects.create(
            nombre='Permiso de Prueba'
        )
        self.assertEqual(permiso.codigo, 'permiso_de_prueba')

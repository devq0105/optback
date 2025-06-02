from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Permiso, Rol, Sucursal
from django.core.validators import RegexValidator

Usuario = get_user_model()

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'nombre', 'codigo', 'descripcion', 'activo', 'creado_en', 'actualizado_en']
        read_only_fields = ['codigo', 'creado_en', 'actualizado_en']
        extra_kwargs = {
            'codigo': {
                'validators': [
                    RegexValidator(
                        regex='^[a-z_]+$',
                        message='Error: El código solo puede contener letras minúsculas y guiones bajos'
                    )
                ]
            },
            'nombre': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este nombre'
                },
                'required': False
            },
            'descripcion': {
                'required': False
            },
            'activo': {
                'required': False
            }
        }

    def validate_nombre(self, value):
        if not value and not self.instance:
            raise serializers.ValidationError("Error: El nombre es requerido para crear un nuevo permiso")
        if value and Permiso.objects.filter(nombre=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Error: Ya existe un registro con este nombre")
        return value

class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(many=True, read_only=True)
    permisos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permiso.objects.all(),
        write_only=True,
        many=True,
        required=False,
        source='permisos'
    )
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'permisos', 'permisos_ids', 'descripcion']
        extra_kwargs = {
            'nombre': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este nombre'
                }
            }
        }

    def validate_nombre(self, value):
        if Rol.objects.filter(nombre=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Error: Ya existe un registro con este nombre")
        return value

    def create(self, validated_data):
        permisos = validated_data.pop('permisos', [])
        rol = Rol.objects.create(**validated_data)
        if permisos:
            rol.permisos.set(permisos)
        return rol

    def update(self, instance, validated_data):
        permisos = validated_data.pop('permisos', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permisos is not None:
            instance.permisos.set(permisos)
        return instance

class SucursalSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.CharField(source='responsable.nombre_completo', read_only=True)
    
    class Meta:
        model = Sucursal
        fields = ['id', 'nombre', 'direccion', 'telefono', 'responsable', 'responsable_nombre', 'activo', 'creado_en', 'actualizado_en']
        read_only_fields = ['creado_en', 'actualizado_en']
        extra_kwargs = {
            'nombre': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este nombre'
                }
            }
        }

class SucursalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ['nombre', 'direccion', 'telefono', 'responsable', 'activo']
        extra_kwargs = {
            'nombre': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este nombre'
                }
            }
        }

    def validate_telefono(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Error: El teléfono solo debe contener números")
        if len(value) < 10:
            raise serializers.ValidationError("Error: El teléfono debe tener al menos 10 dígitos")
        return value

    def validate_nombre(self, value):
        if Sucursal.objects.filter(nombre=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Error: Ya existe un registro con este nombre")
        return value

class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre_completo', 'email', 'fotografia',
            'rol', 'rol_nombre', 'sucursal', 'sucursal_nombre',
            'is_active', 'is_staff', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este email'
                }
            },
            'username': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este nombre de usuario'
                }
            }
        }

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Error: Ya existe un registro con este email")
        return value

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Error: Ya existe un registro con este nombre de usuario")
        return value

class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirmar_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'password', 'confirmar_password',
            'nombre_completo', 'email', 'fotografia',
            'rol', 'sucursal'
        ]
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este email'
                }
            },
            'username': {
                'error_messages': {
                    'unique': 'Error: Ya existe un registro con este nombre de usuario'
                }
            }
        }
    
    def validate(self, data):
        if data['password'] != data['confirmar_password']:
            raise serializers.ValidationError({
                'confirmar_password': 'Error: Las contraseñas no coinciden'
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirmar_password')
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario 
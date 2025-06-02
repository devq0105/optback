from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import re

class Permiso(models.Model):
    nombre = models.CharField(_('nombre'), max_length=100, unique=True)
    codigo = models.CharField(_('código'), max_length=50, unique=True, blank=True)
    descripcion = models.TextField(_('descripción'), blank=True)
    activo = models.BooleanField(_('activo'), default=True)
    creado_en = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    actualizado_en = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('permiso')
        verbose_name_plural = _('permisos')
        ordering = ['nombre']

    def _generar_codigo(self):
        # Convertir el nombre a minúsculas y reemplazar espacios por guiones bajos
        codigo = self.nombre.lower()
        # Reemplazar caracteres especiales y acentos
        codigo = re.sub(r'[áéíóúüñ]', lambda m: {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n'
        }[m.group(0)], codigo)
        # Eliminar caracteres no permitidos
        codigo = re.sub(r'[^a-z0-9_]', '_', codigo)
        # Eliminar guiones bajos múltiples
        codigo = re.sub(r'_+', '_', codigo)
        # Eliminar guiones bajos al inicio y final
        codigo = codigo.strip('_')
        return codigo

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generar_codigo()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(_('nombre'), max_length=100, unique=True)
    permisos = models.ManyToManyField(
        Permiso,
        verbose_name=_('permisos'),
        related_name='roles'
    )
    descripcion = models.TextField(_('descripción'), blank=True)
    activo = models.BooleanField(_('activo'), default=True)

    class Meta:
        verbose_name = _('rol')
        verbose_name_plural = _('roles')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Sucursal(models.Model):
    nombre = models.CharField(_('nombre'), max_length=100)
    direccion = models.TextField(_('dirección'))
    telefono = models.CharField(_('teléfono'), max_length=20)
    responsable = models.ForeignKey(
        'Usuario',
        verbose_name=_('responsable'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sucursales_administradas'
    )
    activo = models.BooleanField(_('activo'), default=True)
    creado_en = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    actualizado_en = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('sucursal')
        verbose_name_plural = _('sucursales')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    nombre_completo = models.CharField(_('nombre completo'), max_length=255)
    fotografia = models.ImageField(_('fotografía'), upload_to='usuarios/fotografias/', null=True, blank=True)
    rol = models.ForeignKey(
        Rol,
        verbose_name=_('rol'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='usuarios'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name=_('sucursal'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='usuarios'
    )
    creado_en = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    actualizado_en = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['username']

    def __str__(self):
        return self.nombre_completo

    def tiene_permiso(self, permiso, obj=None):
        if self.is_superuser:
            return True
        if not self.rol:
            return False
        return self.rol.permisos.filter(codigo=permiso).exists()

    # Método original para compatibilidad con Django
    def has_perm(self, perm, obj=None):
        return self.tiene_permiso(perm, obj) 
from django.db import models

class Equipo(models.Model):
    nombre = models.CharField(max_length=100,null=True)
    tipo = models.CharField(max_length=50,null=True)
    marca = models.CharField(max_length=50,null=True)
    modelo = models.CharField(max_length=50,null=True)
    serie = models.CharField(max_length=50, unique=True,null=True)
    ubicacion = models.CharField(max_length=100,null=True)
    fecha_adquisicion = models.DateField(null=True)
    estado_operativo = models.CharField(max_length=20,null=True)

    def __str__(self):
        return self.nombre

class Mantenimiento(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    fecha_programada = models.DateField()
    fecha_realizada = models.DateField(null=True, blank=True)
    tecnico = models.CharField(max_length=100)
    observaciones = models.TextField()

    def __str__(self):
        return f"{self.tipo} - {self.equipo.nombre}"

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=20)
    contraseña_encriptada = models.CharField(max_length=128)

    def __str__(self):
        return self.nombre

class HistorialOperatividad(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.estado} - {self.equipo.nombre} ({self.fecha_hora})"

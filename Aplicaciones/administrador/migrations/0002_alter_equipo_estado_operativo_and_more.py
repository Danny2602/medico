# Generated by Django 5.1.2 on 2025-06-29 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrador', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipo',
            name='estado_operativo',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='fecha_adquisicion',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='marca',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='modelo',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='nombre',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='serie',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='tipo',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='ubicacion',
            field=models.CharField(max_length=100, null=True),
        ),
    ]

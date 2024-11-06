# Generated by Django 4.0.7 on 2024-11-06 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0006_loctype_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='installation',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locationinstallations', to='installations.location'),
        ),
        migrations.AddField(
            model_name='system',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locationsystems', to='installations.location'),
        ),
    ]

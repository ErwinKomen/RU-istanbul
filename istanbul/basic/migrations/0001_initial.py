# Generated by Django 4.0.7 on 2024-09-04 10:11

import basic.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=200, verbose_name='IP address')),
                ('reason', models.TextField(verbose_name='Reason')),
                ('created', models.DateTimeField(default=basic.models.get_current_datetime)),
                ('path', models.TextField(blank=True, null=True, verbose_name='Path')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Body')),
            ],
        ),
        migrations.CreateModel(
            name='UserSearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view', models.CharField(max_length=255, verbose_name='Listview')),
                ('params', models.TextField(default='[]', verbose_name='Parameters')),
                ('count', models.IntegerField(default=0, verbose_name='Count')),
                ('history', models.TextField(default='{}', verbose_name='History')),
            ],
            options={
                'verbose_name': 'User search',
                'verbose_name_plural': 'User searches',
            },
        ),
    ]

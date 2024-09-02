# Generated by Django 4.1 on 2023-03-28 14:14

import btchub.basic.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0002_alter_usersearch_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=200, verbose_name='IP address')),
                ('reason', models.TextField(verbose_name='Reason')),
                ('created', models.DateTimeField(default=btchub.basic.models.get_current_datetime)),
                ('path', models.TextField(blank=True, null=True, verbose_name='Path')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Body')),
            ],
        ),
    ]

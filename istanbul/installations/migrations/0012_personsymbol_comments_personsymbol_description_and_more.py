# Generated by Django 4.0.7 on 2024-12-04 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0011_personsymbol_persontype_person_ptype'),
    ]

    operations = [
        migrations.AddField(
            model_name='personsymbol',
            name='comments',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='personsymbol',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='persontype',
            name='comments',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='persontype',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
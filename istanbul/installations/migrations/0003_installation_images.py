# Generated by Django 4.0.7 on 2022-10-14 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0002_rename_description_literature_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='installation',
            name='images',
            field=models.ManyToManyField(blank=True, default=None, to='installations.image'),
        ),
    ]

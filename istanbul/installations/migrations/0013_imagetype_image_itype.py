# Generated by Django 4.0.7 on 2024-12-11 07:54

from django.db import migrations, models
import django.db.models.deletion
import utils.model_util


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0012_personsymbol_comments_personsymbol_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('description', models.TextField(default='')),
                ('comments', models.TextField(default='')),
            ],
            bases=(models.Model, utils.model_util.info),
        ),
        migrations.AddField(
            model_name='image',
            name='itype',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='itype_images', to='installations.imagetype'),
        ),
    ]

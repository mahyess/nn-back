# Generated by Django 2.2.2 on 2022-02-14 11:00

from django.db import migrations, models
import namastenepal.community.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=1000, null=True)),
                ('background', models.ImageField(blank=True, height_field='height_field', null=True, upload_to=namastenepal.community.models.get_path, width_field='width_field')),
                ('width_field', models.IntegerField(default=0)),
                ('height_field', models.IntegerField(default=0)),
                ('description', models.TextField()),
                ('icon', models.ImageField(blank=True, height_field='height_field', null=True, upload_to=namastenepal.community.models.get_path, width_field='width_field')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_private', models.BooleanField(default=False)),
                ('priority', models.CharField(choices=[('cr', 'Critical'), ('vh', 'Very_high'), ('hi', 'High'), ('md', 'Medium'), ('lo', 'Low')], default='md', max_length=2)),
            ],
            options={
                'verbose_name': 'samaj',
            },
        ),
        migrations.CreateModel(
            name='CommunityRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000, unique=True)),
                ('description', models.TextField()),
                ('width_field', models.IntegerField(default=0)),
                ('height_field', models.IntegerField(default=0)),
                ('background', models.ImageField(blank=True, height_field='height_field', null=True, upload_to=namastenepal.community.models.get_path, width_field='width_field')),
                ('icon', models.ImageField(blank=True, height_field='height_field', null=True, upload_to=namastenepal.community.models.get_path, width_field='width_field')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('rq', 'Requested'), ('dc', 'Declined'), ('ac', 'Accepted')], default='rq', max_length=2)),
            ],
            options={
                'verbose_name': 'samaj request',
            },
        ),
    ]

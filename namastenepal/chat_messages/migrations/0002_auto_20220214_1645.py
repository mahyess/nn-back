# Generated by Django 2.2.2 on 2022-02-14 11:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chat_messages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='authored_group_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='messages', to='chat_messages.ChatUsersGroup'),
        ),
        migrations.AddField(
            model_name='chatusersgroupprofile',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='message_users_group_admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatusersgroupprofile',
            name='user_group',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='group_profile', to='chat_messages.ChatUsersGroup'),
        ),
        migrations.AddField(
            model_name='chatusersgroup',
            name='participants',
            field=models.ManyToManyField(related_name='users_group_participants', to=settings.AUTH_USER_MODEL),
        ),
    ]

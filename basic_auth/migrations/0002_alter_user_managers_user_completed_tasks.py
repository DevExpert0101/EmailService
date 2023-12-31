# Generated by Django 4.0 on 2023-04-08 23:23

import basic_auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', basic_auth.models.CustomUserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='completed_tasks',
            field=models.JSONField(default=list),
        ),
    ]

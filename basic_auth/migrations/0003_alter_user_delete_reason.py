# Generated by Django 4.0 on 2023-04-10 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_auth', '0002_alter_user_managers_user_completed_tasks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='delete_reason',
            field=models.TextField(blank=True),
        ),
    ]
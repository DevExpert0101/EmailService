# Generated by Django 4.0 on 2023-05-12 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_auth', '0004_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.FileField(default=None, null=True, upload_to='avatar'),
        ),
    ]

# Generated by Django 4.0 on 2023-05-20 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_auth', '0006_userplan_verify_credits'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='verify_credits',
            field=models.IntegerField(default=0),
        ),
    ]

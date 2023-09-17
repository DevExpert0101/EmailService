# Generated by Django 4.0 on 2022-01-06 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_user_is_verified_user_token'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddField(
            model_name='user',
            name='unverified_changed_email',
            field=models.CharField(default=None, max_length=265, null=True),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['unverified_changed_email'], name='api_user_unverif_9c7425_idx'),
        ),
    ]
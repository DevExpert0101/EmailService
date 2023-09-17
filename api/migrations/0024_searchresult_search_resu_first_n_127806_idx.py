# Generated by Django 4.0 on 2023-05-02 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_alter_emailfinderhistory_search_result_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='searchresult',
            index=models.Index(fields=['first_name', 'last_name', 'domain_name'], name='search_resu_first_n_127806_idx'),
        ),
    ]
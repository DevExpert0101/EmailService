# Generated by Django 4.0 on 2023-05-02 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_searchresult_from_bulk_search'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailfinderhistory',
            name='search_result',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.searchresult'),
        ),
        migrations.AlterField(
            model_name='searchresult',
            name='middle_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]

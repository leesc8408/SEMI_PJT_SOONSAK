# Generated by Django 3.2.12 on 2022-11-19 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20221118_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='googld_id',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]

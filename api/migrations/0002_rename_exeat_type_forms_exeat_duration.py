# Generated by Django 4.1.6 on 2023-09-22 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forms',
            old_name='exeat_type',
            new_name='exeat_duration',
        ),
    ]
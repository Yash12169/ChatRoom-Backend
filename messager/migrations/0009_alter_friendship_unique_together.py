# Generated by Django 5.0.1 on 2024-01-12 02:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messager', '0008_pendingrequest_message'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendship',
            unique_together=set(),
        ),
    ]

# Generated by Django 5.0.1 on 2024-01-12 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messager', '0010_alter_pendingrequest_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendingrequest',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
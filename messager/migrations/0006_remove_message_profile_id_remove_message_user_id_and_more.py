# Generated by Django 5.0.1 on 2024-01-11 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messager', '0005_message_content_message_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='profile_id',
        ),
        migrations.RemoveField(
            model_name='message',
            name='user_id',
        ),
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(),
        ),
    ]

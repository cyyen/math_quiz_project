# Generated by Django 5.1.3 on 2024-11-15 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='completion_minutes',
            new_name='completion_seconds',
        ),
    ]

# Generated by Django 5.1.6 on 2025-02-12 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_alter_employee_employee_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='face_embedding',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]

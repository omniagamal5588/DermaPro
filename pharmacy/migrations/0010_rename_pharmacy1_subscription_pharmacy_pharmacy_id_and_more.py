# Generated by Django 4.1.7 on 2023-05-27 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0009_alter_medicine_serial_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscription_pharmacy',
            old_name='Pharmacy1',
            new_name='pharmacy_id',
        ),
        migrations.RenameField(
            model_name='subscription_pharmacy',
            old_name='Subscription1',
            new_name='subscription_id',
        ),
    ]
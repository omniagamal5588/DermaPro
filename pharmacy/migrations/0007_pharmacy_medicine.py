# Generated by Django 4.1.7 on 2023-05-27 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0006_delete_pharmacy_medicine'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pharmacy_medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmacy.medicine')),
                ('pharmacy_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmacy.pharmacy')),
            ],
        ),
    ]

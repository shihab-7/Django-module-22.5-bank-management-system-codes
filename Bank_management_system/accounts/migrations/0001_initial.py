# Generated by Django 5.0 on 2023-12-28 21:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('postal_code', models.IntegerField()),
                ('country', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='address', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserBankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(choices=[('Savings', 'Savings'), ('Current', 'Current')], max_length=10)),
                ('account_no', models.ImageField(unique=True, upload_to='')),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('initial_diposite_date', models.DateField(auto_now_add=True)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

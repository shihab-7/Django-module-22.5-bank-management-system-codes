# Generated by Django 5.0 on 2023-12-30 09:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_alter_userbankaccount_account_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('balance_after_transaction', models.DecimalField(decimal_places=2, max_digits=12)),
                ('transaction_type', models.IntegerField(choices=[(1, 'Deposite'), (2, 'Withdrawal'), (3, 'Loan'), (4, 'Loan Paid')], null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('loan_approved', models.BooleanField(default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='accounts.userbankaccount')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]

# Generated by Django 4.1.10 on 2023-07-23 17:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CasiniLoanApp", "0002_accounttransaction_remove_loan_emi_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="aadhar_id",
            field=models.UUIDField(),
        ),
    ]

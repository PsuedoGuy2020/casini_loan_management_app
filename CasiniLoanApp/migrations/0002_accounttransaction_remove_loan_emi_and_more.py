# Generated by Django 4.1.10 on 2023-07-23 17:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("CasiniLoanApp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("credit", "CREDIT"), ("debit", "DEBIT")],
                        max_length=20,
                    ),
                ),
                ("transaction_date", models.DateTimeField(auto_now_add=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("aadhar_id", models.UUIDField(editable=False)),
            ],
        ),
        migrations.RemoveField(
            model_name="loan",
            name="emi",
        ),
        migrations.AddField(
            model_name="loan",
            name="remaining_amount",
            field=models.PositiveIntegerField(default=20),
        ),
        migrations.AddField(
            model_name="transaction",
            name="remaining_amount",
            field=models.DecimalField(decimal_places=2, default=20, max_digits=10),
        ),
        migrations.AlterField(
            model_name="customer",
            name="credit_score",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="customer",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="loan",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="loan",
            name="start_date",
            field=models.DateField(auto_now=True),
        ),
        migrations.CreateModel(
            name="LoanDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_transaction_date", models.DateTimeField(blank=True, null=True)),
                ("next_emi_date", models.DateField()),
                (
                    "next_emi_amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("initial_emi_amounts", models.CharField(max_length=1000)),
                ("adjusted_emi_amounts", models.CharField(max_length=1000)),
                ("total_emis_left", models.IntegerField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "loan_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="loan",
                        to="CasiniLoanApp.loan",
                    ),
                ),
            ],
        ),
    ]

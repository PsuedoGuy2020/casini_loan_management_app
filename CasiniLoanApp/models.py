from django.db import models
from utils.abstract_models import PrimaryKeyModel


# UserProfile Register Model
class UserProfile(PrimaryKeyModel):
    name = models.CharField(max_length=100)
    email_id = models.EmailField()
    aadhar_id = models.UUIDField(unique=True)
    annual_income = models.DecimalField(max_digits=15, decimal_places=3)
    credit_score = models.IntegerField(null=True, blank=True)

# Storing Loan Details of User
class Loan(PrimaryKeyModel):
    LOAN_CATEGORIES = [
        ("car", "car"),
        ("home", "home"),
        ("education", "education"),
        ("personal", "personal"),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="loan_customers")
    loan_type = models.CharField(max_length=25, choices=LOAN_CATEGORIES)
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField(null=True, blank=True)
    principal_amount = models.PositiveIntegerField()
    interest_rate = models.DecimalField(decimal_places=3, max_digits=15)
    loan_term = models.PositiveIntegerField()
    disbursal_date = models.DateTimeField(auto_now=True)
    rem_amount = models.PositiveIntegerField(default=50)

# Storing Loan Transaction Details of User
class LoanTransactionDetail(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="loan")
    init_emi_amounts = models.CharField(max_length=1000)
    is_active = models.BooleanField(default=True)
    last_txn_date = models.DateTimeField(blank=True, null=True)
    new_emi_date = models.DateField(blank=True, null=True)
    new_emi_amt = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    emi_rem = models.IntegerField()

# Storing User Transactions Info
class TransactionStore(models.Model):
    TRANSACTION_CHOICES = [
        ("credit", "CREDIT"),
        ("debit", "DEBIT"),
    ]

    aadhar_id = models.UUIDField(editable=False)
    amount = models.DecimalField(max_digits=15, decimal_places=3)
    transaction_type = models.CharField(choices=TRANSACTION_CHOICES, max_length=20)
    transaction_date = models.DateTimeField(auto_now_add=True)

# Storing EMI Transaction of User.
class EMITransaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="user_transaction")
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="loan_transaction")
    payment = models.DecimalField(max_digits=15, decimal_places=3)
    payment_date = models.DateTimeField(auto_now=True)

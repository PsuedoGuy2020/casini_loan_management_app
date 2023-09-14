from rest_framework import serializers
from .models import UserProfile, Loan, LoanTransactionDetail

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields='__all__'

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name', 'email')

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ("loan_type", "interest_rate")

class LoanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanTransactionDetail
        fields = ["loan_id"]

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('loan_type', 'loan_amount', 'interest_rate', 'term_period', 'disbursement_date', 'emi_amount')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanDetailSerializer
        fields = ( 'aadhar_id', 'transaction_date', 'amount', 'transaction_type')

class ApplyLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('loan_type', 'loan_amount')

class MakePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanDetailSerializer
        fields = ('aadhar_id', 'transaction_date', 'amount', 'transaction_type')
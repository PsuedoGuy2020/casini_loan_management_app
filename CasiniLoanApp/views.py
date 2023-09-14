import math
from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserSerializer, LoanSerializer, LoanDetailSerializer
from .models import UserProfile, Loan, TransactionStore, LoanTransactionDetail
from json import JSONDecodeError
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# (POST) User Registration View Api
class UserViewApi(APIView):
    get_auth = (TokenAuthentication,)
    get_permission = (IsAuthenticated,)

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            return self.create_user(data)
        except JSONDecodeError:
            return Response(
                {"result": "error", "message": "Json decoding error!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create_user(self, data):
        try:
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            user = self.save_user(data)

            response_data = {
                "id": user.id,
                "message": "User registered successfully!",
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except JSONDecodeError:
            return Response(
                {"result": "error", "message": "Json decoding error!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def save_user(self, data):
        return UserProfile.objects.create(
            name=data["name"],
            email_id=data["email_id"],
            aadhar_id=data["aadhar_id"],
            annual_income=data["annual_income"],
        )

# (POST) Loan Apply View Api
class LoanViewApi(APIView):
    get_auth = (TokenAuthentication,)
    get_permission = (IsAuthenticated,)

    LOAN_CATEGORIES = {
        "car": 750000,
        "home": 8500000,
        "educational": 5000000,
        "personal": 1000000,
    }

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = LoanSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                response = self.process_loan_application(data)
                return Response(response, status=status.HTTP_200_OK)
            else:
                error_message = serializer.errors
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response(
                {"result": "error", "message": "Json decoding error!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def process_loan_application(self, data):
        user_id = data["unique_user_id"]
        loan_type = data["loan_type"]
        principal_amount = data["loan_amount"]
        interest_rate = data["interest_rate"]
        loan_term = data["term_period"]
        disbursal_date = data["disbursement_date"]

        user, loan = self.get_user_and_loan(user_id)

        if interest_rate < 14:
            return {"error": "Interest rate should be greater than 14%!"}, status.HTTP_400_BAD_REQUEST

        if not user:
            return {"error": "User does not exist!"}, status.HTTP_400_BAD_REQUEST

        if not loan:
            if self.check_user_eligibility(user):
                emi_details = self.calculate_emi(
                    user, principal_amount, interest_rate, loan_term, disbursal_date
                )
                loan = self.create_loan(user, loan_type, emi_details)
                response = {
                    "loan_id": loan.id,
                    "due_dates": emi_details["due_dates"],
                }
                return response
            else:
                return {"error": "User is not eligible for the loan!"}, status.HTTP_400_BAD_REQUEST
        else:
            return {"error": "User previous loan already exists!"}, status.HTTP_400_BAD_REQUEST

    def get_user_and_loan(self, user_id):
        try:
            user = UserProfile.objects.get(id=user_id)
            loan = Loan.objects.filter(user_id=user.id).first()
            return user, loan
        except UserProfile.DoesNotExist:
            return None, None

    def check_user_eligibility(self, user):
        if user.credit_score < 450 or user.credit_score is None:
            return False
        elif user.annual_income < 150000:
            return False
        return True

    def calculate_emi(self, user, principal_amount, interest_rate, loan_term, disbursal_date):
        rate = (interest_rate / 12) / 100
        emi_amount = (principal_amount * rate * math.pow((1 + rate), loan_term)) / (
            math.pow((1 + rate), loan_term) - 1
        )
        monthly_emi = round(emi_amount, 2)
        total_recoverable_amount = monthly_emi * loan_term

        if monthly_emi > (Decimal(0.6) * user.annual_income):
            return {"error": "EMI amount exceeds 60% of annual income"}, status.HTTP_400_BAD_REQUEST

        emi_details = self.generate_emi_schedule(
            loan_term, disbursal_date, monthly_emi, total_recoverable_amount
        )

        return emi_details

    def generate_emi_schedule(self, loan_term, disbursal_date, monthly_emi, total_recoverable_amount):
        emi_start_date = disbursal_date + relativedelta(day=1, months=1)

        emi_amount_list = [monthly_emi] * (loan_term - 1)
        emi_due_date_list = [
            emi_start_date + relativedelta(day=1, months=i)
            for i in range(loan_term - 1)
        ]
        due_dates = [
            {
                "date": emi_start_date + relativedelta(day=1, months=i),
                "amount_due": monthly_emi,
            }
            for i in range(loan_term - 1)
        ]

        remaining_amount = total_recoverable_amount - sum(emi_amount_list)

        if remaining_amount > 0:
            emi_amount_list.append(remaining_amount)
            emi_due_date_list.append(
                emi_start_date + relativedelta(day=1, months=loan_term - 1)
            )
            due_dates.append(
                {
                    "date": emi_start_date + relativedelta(day=1, months=loan_term - 1),
                    "amount_due": remaining_amount,
                }
            )

        return {"due_dates": due_dates}

    def create_loan(self, user, loan_type, emi_details):
        disbursal_date_dtf = datetime.strptime(emi_details["disbursement_date"], "%d-%m-%Y")
        loan = Loan.objects.create(
            loan_type=loan_type,
            loan_term=emi_details["loan_term"],
            principal_amount=emi_details["principal_amount"],
            interest_rate=emi_details["interest_rate"],
            disbursal_date=disbursal_date_dtf,
            start_date=datetime.now(),
            user_id=user.id,
            remaining_amount=emi_details["total_recoverable_amount"],
        )

        loan_detail = LoanTransactionDetail.objects.create(
            loan_id_id=loan.id,
            next_emi_date=emi_details["due_dates"][0]["date"],
            next_emi_amount=emi_details["due_dates"][0]["amount_due"],
            total_emis_left=len(emi_details["due_dates"]),
            is_active=True,
        )

        return loan, loan_detail

# (POST) Loan Payment View Api
class PaymentViewApi(APIView):
    get_auth = (TokenAuthentication,)
    get_permission = (IsAuthenticated,)

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            return self.make_loan_payment(data)
        except JSONDecodeError:
            return Response(
                {"result": "error", "message": "Json decoding error"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def make_loan_payment(self, data):
        try:
            serializer = LoanDetailSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            loan, loan_details = self.get_loan_and_details(data["loan_id"])

            if not loan or not loan_details:
                return Response(
                    {"error": "Invalid Loan Id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if self.is_payment_already_made(loan_details):
                return Response(
                    {"error": "Payment already made"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment_amount = data["amount"]
            user = loan.user

            self.create_transaction(payment_amount, user, loan)

            if payment_amount != loan_details.next_emi_amount:
                self.update_next_emi_amount(loan, loan_details, payment_amount)

            self.update_loan_details(loan_details)

            response_data = {
                "loan_id": loan.id,
                "message": "Payment successfully received",
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Invalid Loan Id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_loan_and_details(self, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
            loan_details = LoanTransactionDetail.objects.get(loan_id=loan.id)
            return loan, loan_details
        except ObjectDoesNotExist:
            return None, None

    def is_payment_already_made(self, loan_details):
        today = datetime.now()
        last_txn = loan_details.last_transaction_date

        if last_txn is not None:
            if (
                last_txn.strftime("%m") == today.month
                and last_txn.strftime("%Y") == today.year
            ):
                return True
            elif (today - last_txn).month > 1:
                return True
        return False

    def create_transaction(self, payment_amount, user, loan):
        today = datetime.now()
        TransactionStore.objects.create(
            payment=payment_amount,
            user=user,
            loan=loan,
            payment_date=today,
        )
        loan.remaining_amount -= payment_amount
        loan.save()

    def update_next_emi_amount(self, loan, loan_details, payment_amount):
        rate = Decimal((loan.interest_rate / 12) / 100)
        emi_amount = (
            (loan.remaining_amount - payment_amount)
            * rate
            * Decimal(math.pow((1 + rate), loan.loan_term))
            / Decimal(math.pow((1 + rate), loan.loan_term) - 1)
        )
        loan_details.next_emi_amount = emi_amount

    def update_loan_details(self, loan_details):
        today = datetime.now()
        loan_details.last_transaction_date = today
        loan_details.next_emi_date = today + relativedelta(day=1, months=1)
        loan_details.total_emis_left -= 1

        if loan_details.total_emis_left == 0:
            loan_details.is_active = False

        loan_details.save()

# (GET) Loan Statement View Api
class StatementViewApi(APIView):
    authentication = (TokenAuthentication,)
    permission = (IsAuthenticated,)

    def get(self, request):
        try:
            data = JSONParser().parse(request)
            return self.get_loan_statement(data)
        except JSONDecodeError:
            return Response(
                {"result": "error", "message": "Json decoding error"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_loan_statement(self, data):
        try:
            serializer = LoanDetailSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            loan = self.get_loan(data["loan_id"])
            loan_details = LoanTransactionDetail.objects.get(loan_id=loan.id)
            
            if not loan_details.is_active:
                return Response(
                    {"error": "Loan is not in Active State"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_txn = self.get_user_txn(loan)
            
            if not user_txn:
                upcoming_transactions = self.calculate_upcoming_transactions(loan, loan_details)
                return Response(
                    {"prev_txn": [], "upcoming_transactions": upcoming_transactions},
                    status=status.HTTP_200_OK,
                )

            prev_txn = self.get_prev_txn(user_txn, loan)
            
            response = {
                "prev_txn": prev_txn,
                "upcoming_transactions": self.calculate_upcoming_transactions(loan, loan_details),
            }

            return Response(response, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Loan doesn't exist. Passed Loan id is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_loan(self, loan_id):
        return Loan.objects.get(id=loan_id)

    def get_user_txn(self, loan):
        return TransactionStore.objects.filter(
            user_id=loan.user.id,
            loan_id=loan.id,
        )

    def calculate_upcoming_transactions(self, loan, loan_details):
        monthly_emi = loan.remaining_amount / loan_details.total_emis_left
        disbursal_date_dtf = datetime.strptime(loan.disbursal_date, "%d-%m-%Y")
        emi_start_date = disbursal_date_dtf + relativedelta(day=1, months=1)
        upcoming = []

        for i in range(loan_details.total_emis_left):
            data = {}
            data["amount_due"] = monthly_emi
            data["emi_date"] = emi_start_date + relativedelta(day=1, months=i)
            upcoming.append(data)

        return upcoming

    def get_prev_txn(self, user_txn, loan):
        prev_txn = []
        for txn in user_txn:
            past_txn = {}
            past_txn["date"] = txn.payment_date
            past_txn["amount_paid"] = txn.payment
            past_txn["interest"] = loan.interest_rate
            past_txn["principal"] = loan.remaining_amount
            prev_txn.append(past_txn)
        return prev_txn
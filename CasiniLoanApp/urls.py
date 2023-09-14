from django.urls import path

from CasiniLoanApp.views import (
    UserViewApi,
    LoanViewApi,
    PaymentViewApi,
    StatementViewApi,
)

urlpatterns = [
    path("register-user/", UserViewApi.as_view(), name="register_user"),
    path("apply-loan/", LoanViewApi.as_view(), name="apply_loan"),
    path("make-payment/", PaymentViewApi.as_view(), name="make_payment"),
    path("get-statement/", StatementViewApi.as_view(), name="get_statement"),
]

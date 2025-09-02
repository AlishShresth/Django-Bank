from django.urls import path
from .views import (
    AccountVerificationView,
    DepositView,
    InitiateWithdrawalView,
    VerifyUsernameAndWithdrawAPIView,
    InitiateTransferView,
    VerifyOTPView,
    VerifySecurityQuestionView,
    AccountListAPIView,
    AccountDetailAPIView,
    TransactionListAPIView,
    TransactionPDFView,
)

urlpatterns = [
    path("accounts/", AccountListAPIView.as_view(), name="all_accounts"),
    path("accounts/<uuid:pk>", AccountDetailAPIView.as_view(), name="get_account"),
    path(
        "verify/<uuid:pk>/",
        AccountVerificationView.as_view(),
        name="account_verification",
    ),
    path("deposit/", DepositView.as_view(), name="account_deposit"),
    path(
        "withdrawal/initiate/",
        InitiateWithdrawalView.as_view(),
        name="initiate_withdrawal",
    ),
    path(
        "withdrawal/verify-username/",
        VerifyUsernameAndWithdrawAPIView.as_view(),
        name="verify_username_and_withdraw",
    ),
    path(
        "transfer/initiate/", InitiateTransferView.as_view(), name="initiate_transfer"
    ),
    path(
        "transfer/verify-security-question/",
        VerifySecurityQuestionView.as_view(),
        name="verify_security_question",
    ),
    path("transfer/verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("transactions/", TransactionListAPIView.as_view(), name="transaction_list"),
    path("transactions/pdf/", TransactionPDFView.as_view(), name="transaction_pdf"),
]

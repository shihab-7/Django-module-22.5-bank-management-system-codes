from django.urls import path
from .views import DepositeMoneyView, WithdrawMoneyView, LoanListView, LoanRequestView, TransactionReportView, PayLoanView, TransferMoneyView

urlpatterns = [
    path('deposite/',DepositeMoneyView.as_view(), name='deposite'),
    path('withdraw/',WithdrawMoneyView.as_view(), name='withdraw'),
    path('loan_request/',LoanRequestView.as_view(), name='loan_request'),
    path('loan_list/',LoanListView.as_view(), name='loan_list'),
    path('pay_loan/<int:loan_id>/',PayLoanView.as_view(), name='pay_loan'),
    path('transaction_report/',TransactionReportView.as_view(), name='transaction_report'),
    path('transfer_money/',TransferMoneyView.as_view(), name='transfer_money'),
]

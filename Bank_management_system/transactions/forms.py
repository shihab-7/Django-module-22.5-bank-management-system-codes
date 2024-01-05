from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # account k overriding er jonno niye ashlam
        super().__init__(*args, **kwargs) # override er kaj shuru korte accounts er sob data niye asha hoise super diye
        self.fields['transaction_type'].disabled = True  # ei field ta disabled thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # ei field tar input system hide kore deowa hoilo frontend a

    # akhon save funcion ta k custom modification kore deowa hoilo
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance #new balance add korar por oita update hoye jabe

        return super().save()
    
class DepositeForm(TransactionForm):
    # amount field k filter kora hosse
    def clean_amount(self):
        min_deposite_amount = 100
        amount = self.cleaned_data.get('amount') # user er fillup kora form theke amount field er value niye asha hoilo

        if amount < min_deposite_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposite_amount} $'
            )
        return amount
    

class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance
        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )
        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account'
                'You can not withdraw more than your account balance'
            )
        return amount
    

class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount
    
class TransferMoneyForm(forms.Form):
    transfer_amount = forms.DecimalField()
    receiver_account_no = forms.IntegerField()
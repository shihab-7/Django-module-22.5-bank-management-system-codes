from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from .models import Transaction
from .forms import DepositeForm, WithdrawForm, LoanRequestForm
from .constants import DEPOSITE, WITHDRAWAL,LOAN, LOAN_PAID, TRANSFER, RECEIVE
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from core.models import BankStatus
from .forms import TransferMoneyForm
from accounts.models import UserBankAccount

# Create your views here.
# eita akta base view banay nisi jeta prottek class er vitor inherrit kore code er length komay ana jabe
class TransactionCreateMixin(LoginRequiredMixin, CreateView):

    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

# jokhon e akta new form create hobe tokhon forms.py a amra j constructor diye fields edit er kaj kortesilam __init__ er moddhe oi function a j kwargs er data ta lagto oita amra eikha theke pass kore dissi oita
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account,
        })

        return kwargs
    
    # akoi template use kore ak ak somoy ak ak title diye ak ak kaj korar jonno frontend a title ta bar bar update korar kaj ei function korbe
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title,
        })
        return context



class DepositeMoneyView(TransactionCreateMixin):
    form_class = DepositeForm
    title = 'Deposite Money'

# ei initial data amrai backend theke pass kore dissi frontend a jeta user just dekhte parbe but chose ba edit korte pabe na
    def get_initial(self):
        initial = {'transaction_type': DEPOSITE}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        # user jokhon e valid balance diye form submit dibe tokhon e balance field er value update hoye jabe
        account.save(
            update_fields = ['balance']
        )

        messages.success(self.request, f'{amount} $ is deposited successfully in your account')
        
        return super().form_valid(form)
    

class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

# ei initial data amrai backend theke pass kore dissi frontend a jeta user just dekhte parbe but chose ba edit korte pabe na
    def get_initial(self):

        # bank_status = BankStatus.objects.all().first()
        # print(bank_status)

        initial = {'transaction_type': WITHDRAWAL}
        return initial
    
    def form_valid(self, form):

        bank_status = BankStatus.objects.all().first()
        print(bank_status.is_bankrupt)
        if bank_status is not None and bank_status.is_bankrupt:
            messages.error(self.request, 'Sorry you can not withdraw money from the bank because it is Bankrupt')
            return redirect('withdraw')
    
        else:
            amount = form.cleaned_data.get('amount')
            account = self.request.user.account
            account.balance -= amount
            # user jokhon e valid balance diye form submit dibe tokhon e balance field er value update hoye jabe
            account.save(
                update_fields = ['balance']
            )

            messages.success(self.request, f'{amount} $ is withdrew successfully from your account')
            
            return super().form_valid(form)
    

class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

# ei initial data amrai backend theke pass kore dissi frontend a jeta user just dekhte parbe but chose ba edit korte pabe na
    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type = LOAN, loan_approved = True).count()

        if current_loan_count >= 3:
            return HttpResponse("You have Crossed Your Limits")
        messages.success(self.request, f'Loan Request for {amount} $ is sent to admin successfully')
        
        return super().form_valid(form)
    

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0
    context_object_name = 'report_list'

    def get_queryset(self):

        # jodi user kono type transaction filter na kore sob dekhte chay tobe sob dekhabe
        queryset= super().get_queryset().filter(
            account = self.request.user.account
        )

        # frontend theke start date r end date ashbe 
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

      # specific user er jonno date wise history filter kora hosse
        if start_date_str and end_date_str:

            # date string format a asa oita akhon date format a convert kora hoise
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # timestamp boro theke soto porjonto niye filter kora hoise gte te greater than r lte less than
            queryset = queryset.filter(timestamp__date__gte = start_date , timestamp__date__lte = end_date)

            self.balance = Transaction.objects.filter(timestamp__date__gte = start_date, timestamp__date__lte = end_date).aggregate(Sum('amount'))['amount__sum']

        else :
            # filter na korle balance
            self.balance = self.request.user.account.balance

        # return queryset.distinct() #distinct() function dublicate value gulo baad diye dey
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account
        })
        return context
    

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id= loan_id)

# user er loan approved hoile loan pay korbe
        if loan.loan_approved:
            user_account = loan.account
            if loan.amount < user_account.balance: #user er main balance loan er theke beshi hoilei loan pay korte parbe
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            
            else:
                messages.error(self.request, f'Loan amount is greater than available balance')
        return redirect('loan_list')
            

class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' # ei nam ta set kore dilam jate vejal sarai ei nam diye access korte pari data gulo

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type = LOAN)
        return queryset
    

class TransferMoneyView(LoginRequiredMixin, View):
    template_name = 'transactions/transfer_money.html' # login.html template tai edit kore chalay neowa hoise

# get methode diye form ta front end a pass kore deowa hoise
    def get(self, request):
        form = TransferMoneyForm()
        return render(request, self.template_name,{'form': form})

# post methode diye response backend a ana hoise   
    def post(self, request):
        form = TransferMoneyForm(request.POST)

        if form.is_valid():
            sending_user = request.user.account

            send_amount = form.cleaned_data['transfer_amount']
            receiving_user_account_no = form.cleaned_data['receiver_account_no']

            minimum_transfer = 500
            maximum_transfer = 20000

            valid_receiver = UserBankAccount.objects.filter(account_no=receiving_user_account_no).first()

            if valid_receiver is not None:
                
                if sending_user.balance <= 0:
                    messages.error(request, 'You do not have enough money atleast 500$ can be transferred')
                    return render (request, self.template_name, {'form':form, 'title': 'Transfer Money'})
                
                if sending_user.balance < send_amount:
                    messages.error(request, 'You do not have enough money to transfer.')
                    return render (request, self.template_name, {'form':form, 'title': 'Transfer Money'})
                
                if send_amount > maximum_transfer or send_amount >= sending_user.balance:
                    messages.error(request, f'Your current balance is {sending_user.balance}$ and You can not transfer more than {maximum_transfer}$')
                    return render (request, self.template_name, {'form':form, 'title': 'Transfer Money'})
                
                if send_amount < minimum_transfer:
                    messages.error(request, f'You can not transfer less than {minimum_transfer}$')
                    return render (request, self.template_name, {'form':form, 'title': 'Transfer Money'})
                

                sending_user.balance -= send_amount
                sending_user.save()

                # transaction tracking er jonno new objects banano hoise
                sender = Transaction.objects.create(
                    account = sending_user,
                    amount = send_amount,
                    balance_after_transaction = sending_user.balance,
                    transaction_type = TRANSFER,
                )

                valid_receiver.balance += send_amount
                valid_receiver.save()

                receiver = Transaction.objects.create(
                    account = valid_receiver,
                    amount = send_amount,
                    balance_after_transaction = valid_receiver.balance,
                    transaction_type = RECEIVE,
                )

                messages.success(request, f'Transfer amount {send_amount}$ is successfully completed')  
            else:
                messages.error(request, 'Invalid User , Account does not Exist please enter a valid account number.')
                return render (request, self.template_name, {'form':form, 'title': 'Transfer Money'})
            
        return render(request, self.template_name,{'form': form})
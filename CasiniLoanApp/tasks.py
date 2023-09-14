from celery import Celery
from .models import TransactionStore, UserProfile

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

def calculate_credit_score(account_balance):
    if account_balance >= 1000000:
        return 900
    elif account_balance <= 100000:
        return 300
    else:
        return 300 + ((account_balance - 100000) // 15000) * 10

def calculate_credit_total(transactions):
    return sum(transaction.amount for transaction in transactions)

class UserNotFoundException(Exception):
    pass

@app.task
def credit_score_calculate(user_id):
    try:
        user = UserProfile.objects.get(id=user_id)
        credit_transactions = TransactionStore.objects.filter(
            aadhar_id=user.aadhar_id, transaction_type="credit"
        )
        debit_transactions = TransactionStore.objects.filter(
            aadhar_id=user.aadhar_id, transaction_type="debit"
        )

        credit = calculate_credit_total(credit_transactions)
        debit = calculate_credit_total(debit_transactions)

        account_balance = credit - debit

        credit_score = calculate_credit_score(account_balance)

        user.credit_score = credit_score
        user.save()
    except UserProfile.DoesNotExist:
        raise UserNotFoundException(f"user with ID {user_id} does not exist.")
    except Exception as e:
        raise Exception(f"Error while calculating Credit Score: {str(e)}")

if __name__ == "__main__":
    pass


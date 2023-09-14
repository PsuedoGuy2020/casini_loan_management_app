from django.contrib import admin
from . import models

# Models Registration
admin.site.register(models.UserProfile)
admin.site.register(models.Loan)
admin.site.register(models.LoanTransactionDetail)
admin.site.register(models.TransactionStore)
admin.site.register(models.EMITransaction)


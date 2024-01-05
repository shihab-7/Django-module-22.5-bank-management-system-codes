from django.db import models

# Create your models here.
class BankStatus(models.Model):
    is_bankrupt = models.BooleanField(default=False)

    def __str__(self):
        return f'Bankrupt : {self.is_bankrupt}'
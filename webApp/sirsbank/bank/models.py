from django.db import models
from django.contrib.auth.models import User

import uuid

# Create your models here.



class Account(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    balance = models.IntegerField()
    password = models.CharField(max_length=132) #44salt+88password
    accountNumber = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.name + ' ' +str(self.balance) + ' ' +str(self.email) + ' ' + str(self.password) + ' ' + str(self.accountNumber)


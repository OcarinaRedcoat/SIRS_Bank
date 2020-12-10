from django.db import models
from django.contrib.auth.models import User

import uuid

# Create your models here.



class Account(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    balance = models.IntegerField()
    password = models.CharField(max_length=132) #44salt+88password
    accountNumber = models.UUIDField(default = uuid.uuid4, primary_key=True)
    androidID = models.CharField(max_length=200, default="")

    def __str__(self):
        return str(self.accountNumber)

class Session(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    sessionToken = models.CharField(max_length=88)
    issuedIn = models.DateTimeField(auto_now_add=True, blank=True)


class Transaction(models.Model):
    sender = models.ForeignKey(Account, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, related_name="receiver", on_delete=models.CASCADE)
    ammount = models.IntegerField()
    transaction_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    def __str__(self):
        return str(self.sender) + str(self.receiver)

class RandomNumber(models.Model):
    number = models.CharField(max_length=6)
    issuedIn = models.DateTimeField(auto_now_add=True, blank=True)

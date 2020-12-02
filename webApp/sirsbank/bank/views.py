from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from .models import Account

import re
import os
import hashlib
import base64
import random

# Create your views here.
def index(request):
    return render(request, 'bank/index.html')

def account(request, account_id):
    account = get_object_or_404(Account, accountNumber = account_id)
    context = {'name': account.name, 'balance': '{:.2f}'.format(account.balance/100), 
                'acc_number': '{:025d}'.format(account.accountNumber)}
    return render(request, 'bank/account.html', context)

def login(request):
    return render(request, 'bank/login.html')

def enter(request):
    #login the users
    return HttpResponseRedirect(reverse('bank:account', args=(1,)))

def register(request):
    return render(request, 'bank/register.html')

def signup(request):
    r = request.POST
    securePassword = "[a-z][A-Z]"
    password = r.get('password')
    if (password != r.get('password2')):
        return HttpResponse("Passwords don't match")
    elif(len(password)< 8):
        return HttpResponse("Password must be at least 8 chars long")
    elif(re.search("[a-z]+", password) is None):
        return HttpResponse("Password must contain at least one lowercase")
    elif(re.search("[A-Z]+", password) is None):
        return HttpResponse("Password must contain at least one uppercase")
    elif(re.search("[0-9]+", password) is None):
        return HttpResponse("Password must contain at least one digit")
    elif(re.search("[\.,;:\-\+\*/!?%@#&\\_~\^`´\"\'\$\|]+",r.get('password')) is None):
        return HttpResponse("Password must contain at least one special char")

    #check if the user is already registred
    if(Account.objects.filter(email=r.get('email')).exists()):
        return HttpResponse("Email already registred")

    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=64)

    salt_b64 = base64.b64encode(salt)
    salt_string = salt_b64.decode('ascii')

    password_b64 = base64.b64encode(key)
    password_string = password_b64.decode('ascii')

    final_password_string = salt_string + password_string
    
    newAccount = Account()
    newAccount.name = r.get('name')
    newAccount.email = r.get('email')
    newAccount.balance = 0
    newAccount.password = final_password_string

    #iban = '{:025d}'.format(random.randint(0, 9999999999999999999999999))
    iban = random.randint(0,9999999999999999999999999)
    newAccount.accountNumber = iban

    newAccount.save()

    #singup the user
    return HttpResponseRedirect(reverse('bank:account', args=(iban,)))
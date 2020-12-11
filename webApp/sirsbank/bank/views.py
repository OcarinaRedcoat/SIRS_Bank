from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Account
from .models import Session
from .models import Transaction
from .models import RandomNumber

import re
import os
import hashlib
import base64
import random
import datetime

import socket
import json

flag = False

# Create your views here.
def index(request):
    return render(request, 'bank/index.html')

def account(request, account_id):
    account = get_object_or_404(Account, accountNumber = account_id)
    context = {'name': account.name}

    try:
        session = Session.objects.get(account = account)
        rtokenId = request.COOKIES.get('id_token')
        if(rtokenId == session.sessionToken and session.issuedIn + datetime.timedelta(minutes=30) > timezone.now()):
            return render(request, 'bank/account.html', context)
        else:
            return HttpResponseRedirect(reverse('bank:login'))
    except Session.DoesNotExist:
        return HttpResponseRedirect(reverse('bank:login'))


def login(request):
    return render(request, 'bank/login.html')

def enter(request):
    try:
        request = request.POST
        email = request.get('email')
        account = Account.objects.get(email = email)

        userPassword = request.get('password')

        saltNpassword = account.password
        salt = saltNpassword[:44]
        password = saltNpassword[44:]

        salt = salt.encode('ascii')
        salt = base64.b64decode(salt)

        key = hashlib.pbkdf2_hmac('sha256', userPassword.encode('utf-8'), salt, 100000, dklen=64)

        password_b64 = base64.b64encode(key)
        password_string = password_b64.decode('ascii')

        if(password_string != password):
            return HttpResponse("Incorrect password")

        userAndroidID = account.androidID
        if(twoFactorAuth(userAndroidID) == False):
            return HttpResponse("Smartphone Authentication Failed")

        idToken = os.urandom(64)
        idToken = base64.b64encode(idToken)
        idToken = idToken.decode('ascii')

        #A session can already be there, delete it first
        try:
            session = Session.objects.get(account = account)
            session.delete()
        except Session.DoesNotExist: 
            pass

        newSession = Session()
        newSession.account = account
        newSession.sessionToken = idToken
        newSession.save()

        response = HttpResponseRedirect(reverse('bank:account', args=(account.accountNumber,)))
        response.set_cookie('id_token', newSession.sessionToken)
        return response
    except Account.DoesNotExist:
        return HttpResponse("Email not found")


def register(request):
    number = ''.join(["{}".format(random.randint(0, 9))for num in range(0, 6)])
    context = {'number': number}
    randomNum = RandomNumber()
    randomNum.number = number
    return render(request, 'bank/register.html', context)

def logout(request):
    id_token = request.COOKIES.get('id_token')
    try:    
        session = Session.objects.get(sessionToken = id_token)
        session.delete()
        return HttpResponseRedirect(reverse('bank:index'))
    except Session.DoesNotExist: 
        pass

def information(request):
    id_token = request.COOKIES.get('id_token')
    try:    
        session = Session.objects.get(sessionToken = id_token)
        acc = session.account
        return HttpResponseRedirect(reverse('bank:info', args=(acc.accountNumber,)))
    except Session.DoesNotExist: 
        return HttpResponseRedirect(reverse('bank:index'))

def info(request, account_id):
    account = get_object_or_404(Account, accountNumber = account_id)
    try:
        session = Session.objects.get(account = account)
        transaction_list =  Transaction.objects.filter(sender=account) | Transaction.objects.filter(receiver=account)
        print(transaction_list)
        context = {'name': account.name, 'balance': '{:.2f}'.format(account.balance/100), 
                'acc_number': account.accountNumber, 'email' : account.email, 'transaction_list': transaction_list}
        rtokenId = request.COOKIES.get('id_token')
        if(rtokenId == session.sessionToken and session.issuedIn + datetime.timedelta(minutes=30) > timezone.now()):
            return render(request, 'bank/info.html', context)
        else:
            return HttpResponseRedirect(reverse('bank:login'))
    except Session.DoesNotExist:
        return HttpResponseRedirect(reverse('bank:login'))

def deposit(request):
    try:
        rtokenId = request.COOKIES.get('id_token')
        session = Session.objects.get(sessionToken=rtokenId)
        if(rtokenId == session.sessionToken and session.issuedIn + datetime.timedelta(minutes=30) > timezone.now()):
            r = request.POST
            ammount = r.get('ammount')
            acc = session.account
            if(twoFactorAuth(acc.androidID) == False):
                    return HttpResponse("Smartphone Authentication Failed")
            try:
                print("1")
                acc.balance += int(ammount)*100
            except ValueError:
                return HttpResponse('Invalid ammount')
            acc.save()
            print("2")
            t = Transaction()
            t.sender = acc
            t.receiver = acc
            t.ammount = int(ammount)*100
            t.save()
            response = HttpResponseRedirect(reverse('bank:account', args=(acc.accountNumber,)))            
            return response
        else:
            return HttpResponseRedirect(reverse('bank:login'))
    except Session.DoesNotExist:
        return HttpResponseRedirect(reverse('bank:login'))


def back(request):
    try:
        rtokenId = request.COOKIES.get('id_token')
        session = Session.objects.get(sessionToken=rtokenId)
        if(rtokenId == session.sessionToken and session.issuedIn + datetime.timedelta(minutes=30) > timezone.now()):
            acc = session.account
            return HttpResponseRedirect(reverse('bank:account', args=(acc.accountNumber,)))
        else:
            return HttpResponseRedirect(reverse('bank:login'))
    except Session.DoesNotExist:
        return HttpResponseRedirect(reverse('bank:login'))


def transfer(request):
    try:
        rtokenId = request.COOKIES.get('id_token')
        session = Session.objects.get(sessionToken=rtokenId)
        if(rtokenId == session.sessionToken and session.issuedIn + datetime.timedelta(minutes=30) > timezone.now()):
            r = request.POST
            ammount = r.get('ammount') 
            transferTo = r.get('accNumber')
            acc1 = session.account
            try:
                acc2 = Account.objects.get(accountNumber=transferTo)
                try:
                    int(ammount)
                except ValueError:
                    return HttpResponse('Invalid Ammount')
                if(twoFactorAuth(acc1.androidID) == False):
                    return HttpResponse("Smartphone Authentication Failed")
                if(acc1.balance*100 < int(ammount)*100):
                    return HttpResponse('No funds')
                acc1.balance -= int(ammount)*100
                acc2.balance += int(ammount)*100
                acc1.save()
                acc2.save()
                t = Transaction()
                t.sender = acc1
                t.receiver = acc2
                t.ammount = int(ammount)*100
                t.save()
                response = HttpResponseRedirect(reverse('bank:account', args=(acc1.accountNumber,)))            
                return response
            except (Account.DoesNotExist, ValidationError) as e:
                return HttpResponse('Invalid account number')
        else:
            return HttpResponseRedirect(reverse('bank:login'))
    except Session.DoesNotExist:
        return HttpResponseRedirect(reverse('bank:login'))


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


    try:
        controlNumber = RandomNumber.objects.get(number= r.get('number'))
        if (controlNumber.issuedIn + datetime.timedelta(minutes=5) > timezone.now()):
            return HttpResponse("Control number expired")
        if (controlNumber != r.get('number')):
            return HttpResponse("Invalid number")
#######Inserir controlo aqui###################
#######O controlNumber tem o número que queremos verificar###########
######Se falhar o control dar return HttpResponse("Numbers dont match")###
#######Depois lá em baixo apóes fazer newAccount = Account()####
#######Fazer newAccount.androidID = androidID que veio da mensagem#####
#######Sugeria a funcao que verifica devolver o androidID e receber o numero####
#######E depois lá dentro faz a verificaçao se são iguais#####
    except RandomNumber.DoesNotExist:
        return HttpResponse("Control number incorrect")

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

    newAccount.save()
    
    idToken = os.urandom(64)
    idToken = base64.b64encode(idToken)
    idToken = idToken.decode('ascii')

    newSession = Session()
    newSession.account = newAccount
    newSession.sessionToken = idToken
    newSession.save()

    response = HttpResponseRedirect(reverse('bank:account', args=(newAccount.accountNumber,)))
    response.set_cookie('id_token', newSession.sessionToken)
    return response

def twoFactorAuth(userAndroidID):
    print(userAndroidID)
    host, port = "192.168.1.125", 1234
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        client.bind((host, port))
    finally:
        pass
    client.listen(10) # how many connections can it receive at one time

    while True:
        conn, addr = client.accept()
        
        data = conn.recv(1024)
        print(data)

        data_decoded = data.decode("utf-8")
        print(data_decoded)
        dataJson = json.loads(data_decoded)
        print(dataJson['androidID'])
        #print(dataJson[androidID])

        if(userAndroidID == dataJson['androidID']):
            client.close()
            print("2fa")
            return True
        else:
           return False


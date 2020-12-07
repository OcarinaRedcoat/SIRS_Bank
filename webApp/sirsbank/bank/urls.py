from django.urls import path

from . import views

app_name = 'bank'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name="login"),
    path('enter', views.enter, name="enter"),
    path('register', views.register, name="register"),
    path('signup', views.signup, name="signup"),
    path('<uuid:account_id>/', views.account, name='account'),
    path('logout', views.logout, name='logout'),
    path('information', views.information, name='information'),
    path('info/<uuid:account_id>/', views.info, name='info'),
    path('deposit', views.deposit, name='deposit'),
    path('transfer', views.transfer, name='transfer')
]
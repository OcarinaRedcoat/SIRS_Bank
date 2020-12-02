from django.urls import path

from . import views

app_name = 'bank'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name="login"),
    path('enter', views.enter, name="enter"),
    path('register', views.register, name="register"),
    path('signup', views.signup, name="signup"),
    path('<int:account_id>/', views.account, name='account')
]
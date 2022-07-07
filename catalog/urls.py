from django.urls import path, re_path
from . import views

urlpatterns = [
    path("",views.homePage, name="homePage"),
    path('registerUser/', views.registerUser, name='register'),
    path('registerEnterprise/', views.enterpriseRegistration.as_view(), name='registerEnterprise'),
    path('registerInvestor/', views.investorRegistration.as_view(), name='registerInvestor'),
    path('logInUser/', views.logInUser, name='logIn'),
    path('enterpriseView/<str:idUser>/', views.enterpriseView.as_view(), name='enterprisePage'),
    path('enterpriseMarketView/<str:idUser>/', views.enterpriseMarketView.as_view(), name='enterpriseMarketPage'),
    path('investorMarketView/<str:idUser>/', views.investorMarketView.as_view(), name='investorMarketPage'),
    path('sellE/<str:idUser>/', views.enterpriseView.sell, name='sellE'),
    path('buyE/<str:idUser>/', views.enterpriseMarketView.buy, name='buyE'),

    path('buyI/<str:idUser>/', views.investorMarketView.buy, name='buyI'),
    path('sellI/<str:idUser>/', views.investorView.sell, name='sellI'),

    path('investorView/<str:idUser>/', views.investorView.as_view(), name='investorPage'),
    path('logOut/', views.logOutUser, name='logOutUser'),
    path('emit/<str:idUser>/', views.enterpriseView.emitStocks, name='emit'),
]
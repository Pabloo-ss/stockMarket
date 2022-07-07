from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import CreateView
from catalog.forms import BuyForm, EnterpriseSignUpForm, InvestorSignUpForm, LogInForm, SellForm, EmitForm
from catalog.models import Enterprise, Investor, Stocks, User, Market
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.messages import get_messages
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

def homePage (response):
    users = User.objects.all()
    return render(response, "catalog/homePage.html")

def registerUser(request):
    return render(request, "catalog/register.html")


class enterpriseMarketView(LoginRequiredMixin,CreateView):
    model = Stocks
    form_class = EnterpriseSignUpForm
    template_name = "catalog/marketEnterprise.html"
    login_url = '/catalog/logInUser/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super(enterpriseMarketView, self).get_context_data(**kwargs)
        context['enterprise'] = Enterprise.objects.get(user=User.objects.get(idUser=self.kwargs['idUser']))
        context['userId'] = self.kwargs['idUser']
        context['sellForm'] = SellForm()
        context['buyForm'] = BuyForm()
        context['emitForm'] = EmitForm()
        #First table
        stocksEnt = Stocks.objects.filter(idUser=self.kwargs['idUser'])
        stkName = []
        for stk in stocksEnt:
            stkName.append(Enterprise.objects.get(user_id = stk.idEnterprise).companyName)
        stkSh = zip(stocksEnt, stkName)
        context['stocksShow'] = stkSh
        #Second table
        market = Market.objects.filter()
        marketName = []
        for mtk in market:
            marketName.append(Enterprise.objects.get(user_id = mtk.idEnterprise).companyName)
        stkH = zip(market, marketName)
        context['historyShow'] = stkH

        #Number of visits 
        numVisits = self.request.session.get('numVisitsMarket', 0)
        self.request.session['numVisitsMarket'] = numVisits + 1
        context['numVisits'] = numVisits + 1

        return context

    def buy(request, idUser):#we buy the exact amount of stocks wanted, if the buyer does not have money enough the purchase is canceled
        if request.method == 'POST':
            form = BuyForm(request.POST)

            if form.is_valid():
                transaction.set_autocommit(False)
                #getting the enterprise
                enterprise = Enterprise.objects.get(companyName=form.cleaned_data['enterpriseName'])
                #getting the amount of stocks wanted
                desiredCuantity = form.cleaned_data['cuantity']
                #some inizialitations
                stockAcc = 0
                priceAcc = 0
                amountOK = False
                #getting the sell orders avaliable
                sellOrders = Market.objects.filter(idEnterprise=enterprise).order_by('price')#ascending by default
                #buy algorithm
                for order in sellOrders:
                    stockAcc += order.cuantity
                    priceAcc += order.price * order.cuantity
                    #getting the seller 
                    userSell = order.idUser
                    if userSell.isInvestor:
                        seller = Investor.objects.get(user=userSell)
                    else:
                        seller = Enterprise.objects.get(user=userSell)
                    #handling different situations
                    if stockAcc == desiredCuantity:
                        #update seller wallet
                        seller.wallet = seller.wallet + order.cuantity * order.price
                        seller.save()
                        #delete sell order
                        order.delete()
                        amountOK = True
                        break #end the loop
                    elif stockAcc < desiredCuantity:
                        #update seller wallet
                        seller.wallet = seller.wallet + order.cuantity * order.price
                        seller.save()
                        #delete sell order
                        order.delete()
                    else:
                        #how many stocks do we need
                        usedStocks = desiredCuantity - (stockAcc - order.cuantity)
                        #update seller wallet
                        seller.wallet = seller.wallet + usedStocks * order.price
                        seller.save()
                        #update sell order
                        order.cuantity = order.cuantity - usedStocks
                        order.save()
                        amountOK = True
                        #reset price
                        priceAcc = priceAcc - order.price * order.cuantity
                        break #end the loop

                #Check if the amount of stocks needed was reached
                if amountOK:
                    #getting the buyer 
                    user = User.objects.get(pk=idUser)
                    if user.isInvestor:
                        buyer = Investor.objects.get(user=user)
                    else:
                        buyer = Enterprise.objects.get(user=user)
                    #Check if buyer has enough money
                    if buyer.wallet >= priceAcc:
                        #update owness
                        alreadyOwned = Stocks.objects.filter(idUser=user, idEnterprise=enterprise)
                        if alreadyOwned.exists(): #check if buyer already has stocks of that enterprise
                            for owned in alreadyOwned:
                                owned.cuantity =  owned.cuantity + desiredCuantity
                                owned.save()
                        else:
                            stocksUpdate = Stocks.objects.create(idUser=user, idEnterprise=enterprise, cuantity=desiredCuantity)
                            stocksUpdate.save()
                        #update buyer wallet
                        buyer.wallet = buyer.wallet - priceAcc
                        buyer.save()    
                        transaction.commit()
                    else:
                        transaction.rollback() 
                else:
                    transaction.rollback() 
                
                transaction.set_autocommit(True)

        else:
            form = BuyForm()
            
        url = '/catalog/enterpriseMarketView/' + str(idUser)
        return  redirect(url)

class enterpriseView(LoginRequiredMixin,CreateView):
    model = Stocks #y esta lo mismo q la de abaajo
    form_class = EnterpriseSignUpForm #esta linea tiene sentido? en plan sirve para algo?
    template_name = 'catalog/portfolioEnterprise.html'
    login_url = '/catalog/logInUser/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super(enterpriseView, self).get_context_data(**kwargs)
        context['enterprise'] = Enterprise.objects.get(user=User.objects.get(idUser=self.kwargs['idUser']))
        context['userId'] = self.kwargs['idUser']
        context['sellForm'] = SellForm()
        context['emitForm'] = EmitForm()
        context['emitError'] = "none"

        #First table
        stocksEnt = Stocks.objects.filter(idUser=self.kwargs['idUser'])
        stkName = []
        for stk in stocksEnt:
            stkName.append(Enterprise.objects.get(user_id = stk.idEnterprise).companyName)
        #Calculate medium price
        stkPrice = []
        for stk in stocksEnt:
            marketPrices = Market.objects.filter(idEnterprise=stk.idEnterprise)
            priceMed=0
            for r in marketPrices:
                priceMed= priceMed + r.price
            if(marketPrices.count()==0):
                priceMed=priceMed
            else:
                priceMed = priceMed / marketPrices.count()
            
            append=priceMed
            #stkName.append(Enterprise.objects.get(user_id = stk.idEnterprise).companyName)
            stkPrice.append('{0:.4g}'.format(append))
        #Calculate Allocation
        allocation = []
        #first calculate total worth of Portfolio
        totalWorth=0
        for i in range (len(stkPrice)):
            totalWorth = totalWorth + (float(stkPrice[i])*float((stocksEnt[i].cuantity)))
        if totalWorth != 0:
            for i in range(len(stkPrice)):
                allocation.append('{0:.2g}'.format((float(stkPrice[i])*float(stocksEnt[i].cuantity))/totalWorth))
        else:
            for i in range(len(stkPrice)):
                allocation.append(0)

        stkSh = zip(stocksEnt, stkName, stkPrice,allocation)
        #aqui habria que calcular el precio medio en el mercado de las acciones de la empresa
        context['stocksShow'] = stkSh
        #Second table
        market = Market.objects.filter()
        marketName = []
        for mtk in market:
            marketName.append(Enterprise.objects.get(user_id = mtk.idEnterprise).companyName)
        stkH = zip(market, marketName)
        context['historyShow'] = stkH

        #message errors
        #if 'errors' in self.request.session comprobar si un campo de sesiones existe
        #print(self.request.session['errors']) acceder a el

        storage = get_messages(self.request)
        context['messages'] = storage

        #Number of visits 
        numVisits = self.request.session.get('numVisits', 0)
        self.request.session['numVisits'] = numVisits + 1
        context['numVisits'] = numVisits + 1

        return context

    def sell(request, idUser):
        if request.method == 'POST':
            form = SellForm(request.POST)

            if form.is_valid():
                #need to validate cuantity (see if has enough)
                amount = form.cleaned_data['cuantity']
                try:
                    #getting the user, the enterprise and the stocks
                    user = User.objects.get(idUser=idUser)
                    enterprise = Enterprise.objects.get(companyName=form.cleaned_data['enterprise'])
                    ownStocks = Stocks.objects.get(idUser=user, idEnterprise=enterprise)
                    if ownStocks.cuantity >= amount:
                        transaction.set_autocommit(False)
                        price=form.cleaned_data['price']
                        #create sell order
                        sellOrder = Market.objects.create(idUser=user, idEnterprise=enterprise, cuantity=amount, price=price)
                        sellOrder.save()
                        #update seller stocks
                        if ownStocks.cuantity == amount:
                            ownStocks.delete()
                        else:
                            ownStocks.cuantity = ownStocks.cuantity - amount
                            ownStocks.save()
                        transaction.set_autocommit(True)
                    else:
                        print("not enough stocks")
                        messages.error(request, "Not enough stocks to sell.")
                except ObjectDoesNotExist: 
                    print("Invalid company")
                    #request.session['errors'] = "The company name doesn't match. Please introduce a valid company name."
                    messages.error(request, "The company name doesn't match. Please introduce a valid company name.")
        
        url = '/catalog/enterpriseView/' + str(idUser)
        return  redirect(url)
    
    def emitStocks(request, idUser):
        if request.method == 'POST':
            form = EmitForm(request.POST)

            if form.is_valid():
                transaction.set_autocommit(False)
                #getting user object and enterprise object
                user = User.objects.get(idUser=idUser)
                enterprise = Enterprise.objects.get(user=user)
                #la cantidad ya deberia de llegar validada pero no me fio mucho la vdd
                amount = form.cleaned_data['amount']
                #check if we have to update or create a record
                try:
                    alreadyOwned = Stocks.objects.filter(idUser=user, idEnterprise=enterprise).get()
                    alreadyOwned.cuantity =  alreadyOwned.cuantity + amount
                    alreadyOwned.save()
                    transaction.set_autocommit(True)
                except ObjectDoesNotExist: #if this exception raises, it means we have to create a new record
                    stocksUpdate = Stocks.objects.create(idUser=user, idEnterprise=enterprise, cuantity=amount)
                    stocksUpdate.save()
                    transaction.set_autocommit(True)  
        url = '/catalog/enterpriseView/' + str(idUser)
        return  redirect(url)                 

class investorView(LoginRequiredMixin,CreateView):
    model = Stocks
    form_class = InvestorSignUpForm
    template_name = 'catalog/portfolioInvestor.html'
    login_url = '/catalog/logInUser/'
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
        context = super(investorView, self).get_context_data(**kwargs)
        context['investor'] = Investor.objects.get(user=User.objects.get(idUser=self.kwargs['idUser']))
        context['userId'] = self.kwargs['idUser']
        context['sellForm'] = SellForm()
        #context['wallet'] = Investor.objects.get(wallet=User.objects.get(idUser=self.kwargs['idUser']))

        stocksEnt = Stocks.objects.filter(idUser=self.kwargs['idUser'])
        stkName = []
        for stk in stocksEnt:
            stkName.append(Enterprise.objects.get(user_id = stk.idEnterprise).companyName)
        
        #Calculate medium price
        stkPrice = []
        for stk in stocksEnt:
            marketPrices = Market.objects.filter(idEnterprise=stk.idEnterprise)
            priceMed=0
            for r in marketPrices:
                priceMed= priceMed + r.price

            if marketPrices.count() != 0:
                priceMed = priceMed / marketPrices.count()
            else:
                priceMed = 0
            append=priceMed
            #stkName.append(Enterprise.objects.get(user_id = stk.idEnterprise).companyName)
            stkPrice.append('{0:.4g}'.format(append))
        #Calculate Allocation
        allocation = []
        #first calculate total worth of Portfolio
        totalWorth=0
        for i in range (len(stkPrice)):
            totalWorth = totalWorth + (float(stkPrice[i])*float((stocksEnt[i].cuantity)))
        if totalWorth != 0:
            for i in range(len(stkPrice)):
                allocation.append('{0:.2g}'.format((float(stkPrice[i])*float(stocksEnt[i].cuantity))/totalWorth))
        else:
            for i in range(len(stkPrice)):
                allocation.append(0)
        final = zip(stocksEnt, stkName, stkPrice, allocation)
        context['stocksShow'] = final

        #Number of visits 
        numVisits = self.request.session.get('numVisitsMarket', 0)
        self.request.session['numVisitsMarket'] = numVisits + 1
        context['numVisits'] = numVisits + 1
        
        return context

    def sell(request, idUser):
        if request.method == 'POST':
            form = SellForm(request.POST)

            if form.is_valid():
                #need to validate cuantity (see if has enough)
                amount = form.cleaned_data['cuantity']
                try:
                    #getting the user, the enterprise and the stocks
                    user = User.objects.get(idUser=idUser)
                    enterprise = Enterprise.objects.get(companyName=form.cleaned_data['enterprise'])
                    ownStocks = Stocks.objects.get(idUser=user, idEnterprise=enterprise)
                    if ownStocks.cuantity >= amount:
                        transaction.set_autocommit(False)
                        price=form.cleaned_data['price']
                        #create sell order
                        sellOrder = Market.objects.create(idUser=user, idEnterprise=enterprise, cuantity=amount, price=price)
                        sellOrder.save()
                        #update seller stocks
                        if ownStocks.cuantity == amount:
                            ownStocks.delete()
                        else:
                            ownStocks.cuantity = ownStocks.cuantity - amount
                            ownStocks.save()
                        transaction.set_autocommit(True)
                    else:
                        print("not enough stocks")
                        messages.error(request, "Not enough stocks to sell.")
                except ObjectDoesNotExist: #if this exception raises, it means we have to create a new record
                    print("Invalid company")
                    #request.session['errors'] = "The company name doesn't match. Please introduce a valid company name."
                    messages.error(request, "The company name doesn't match. Please introduce a valid company name.")
            url = '/catalog/investorView/' + str(idUser)
            return  redirect(url)


class investorMarketView(LoginRequiredMixin,CreateView):
    model = Stocks
    form_class = InvestorSignUpForm
    template_name = "catalog/marketInvestor.html"
    login_url = '/catalog/logInUser/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super(investorMarketView, self).get_context_data(**kwargs)
        context['investor'] = Investor.objects.get(user=User.objects.get(idUser=self.kwargs['idUser']))
        context['userId'] = self.kwargs['idUser']
        context['buyForm'] = BuyForm()
        #First table
        stocksEnt = Stocks.objects.filter(idUser=self.kwargs['idUser'])
        stkName = []
        for stk in stocksEnt:
            stkName.append(Enterprise.objects.get(user_id = stk.idEnterprise).companyName)
        stkSh = zip(stocksEnt, stkName)
        context['stocksShow'] = stkSh
        #Second table
        market = Market.objects.filter()
        marketName = []
        for mtk in market:
            marketName.append(Enterprise.objects.get(user_id = mtk.idEnterprise).companyName)
        stkH = zip(market, marketName)
        context['historyShow'] = stkH

        #Number of visits 
        numVisits = self.request.session.get('numVisits', 0)
        self.request.session['numVisits'] = numVisits + 1
        context['numVisits'] = numVisits + 1

        return context

    def buy(request, idUser):#we buy the exact amount of stocks wanted, if the buyer does not have money enough the purchase is canceled
        if request.method == 'POST':
            form = BuyForm(request.POST)

            if form.is_valid():
                transaction.set_autocommit(False)
                #getting the enterprise
                enterprise = Enterprise.objects.get(companyName=form.cleaned_data['enterpriseName'])
                #getting the amount of stocks wanted
                desiredCuantity = form.cleaned_data['cuantity']
                #some inizialitations
                stockAcc = 0
                priceAcc = 0
                amountOK = False
                #getting the sell orders avaliable
                sellOrders = Market.objects.filter(idEnterprise=enterprise).order_by('price')#ascending by default
                #buy algorithm
                for order in sellOrders:
                    stockAcc += order.cuantity
                    priceAcc += order.price * order.cuantity
                    #getting the seller 
                    userSell = order.idUser
                    if userSell.isInvestor:
                        seller = Investor.objects.get(user=userSell)
                    else:
                        seller = Enterprise.objects.get(user=userSell)
                    #handling different situations
                    if stockAcc == desiredCuantity:
                        #update seller wallet
                        seller.wallet = seller.wallet + order.cuantity * order.price
                        seller.save()
                        #delete sell order
                        order.delete()
                        amountOK = True
                        break #end the loop
                    elif stockAcc < desiredCuantity:
                        #update seller wallet
                        seller.wallet = seller.wallet + order.cuantity * order.price
                        seller.save()
                        #delete sell order
                        order.delete()
                    else:
                        #how many stocks do we need
                        usedStocks = desiredCuantity - (stockAcc - order.cuantity)
                        #update seller wallet
                        seller.wallet = seller.wallet + usedStocks * order.price
                        seller.save()
                        #update sell order
                        order.cuantity = order.cuantity - usedStocks
                        order.save()
                        amountOK = True
                        #reset price
                        priceAcc = priceAcc - order.price * order.cuantity
                        break #end the loop

                #Check if the amount of stocks needed was reached
                if amountOK:
                    #getting the buyer 
                    user = User.objects.get(pk=idUser)
                    if user.isInvestor:
                        buyer = Investor.objects.get(user=user)
                    else:
                        buyer = Enterprise.objects.get(user=user)
                    #Check if buyer has enough money
                    if buyer.wallet >= priceAcc:
                        #update owness
                        alreadyOwned = Stocks.objects.filter(idUser=user, idEnterprise=enterprise)
                        if alreadyOwned.exists(): #check if buyer already has stocks of that enterprise
                            for owned in alreadyOwned:
                                owned.cuantity =  owned.cuantity + desiredCuantity
                                owned.save()
                        else:
                            stocksUpdate = Stocks.objects.create(idUser=user, idEnterprise=enterprise, cuantity=desiredCuantity)
                            stocksUpdate.save()
                        #update buyer wallet
                        buyer.wallet = buyer.wallet - priceAcc
                        buyer.save()    
                        transaction.commit()
                    else:
                        transaction.rollback() 
                else:
                    transaction.rollback() 
                
                transaction.set_autocommit(True)

        else:
            form = BuyForm()
            
        url = '/catalog/investorMarketView/' + str(idUser)
        return  redirect(url)

class enterpriseRegistration(CreateView):
    model = User
    form_class = EnterpriseSignUpForm
    template_name = 'catalog/registerEnterprise.html'

    def get_context_data(self, **kwargs):
        context = super(investorMarketView, self).get_context_data(**kwargs)

        storage = get_messages(self.request)
        context['messages'] = storage

        return context

    def form_valid(self, form):
        #we need to know if passwords are alike
        if(form.cleaned_data.get('password') == form.cleaned_data.get('password2')):
            user = form.save()
            login(self.request, user)
            url = '/catalog/enterpriseView/' + str(user.idUser)
            return  redirect(url)
        else:
            url = 'registerEnterprise/'
            messages.error(self.request, "Passwords must match.")
            return  redirect(url)
        

class investorRegistration(CreateView):
    model = User
    form_class = InvestorSignUpForm
    template_name = 'catalog/registerInvestor.html'

    def get_context_data(self, **kwargs):
        context = super(investorMarketView, self).get_context_data(**kwargs)

        storage = get_messages(self.request)
        context['messages'] = storage

        return context

    def form_valid(self, form):
        #we need to know if the passwords are alike
        if(form.cleaned_data.get('password') == form.cleaned_data.get('password2')):
            user = form.save()
            login(self.request, user)
            url = '/catalog/investorView/' + str(user.idUser)
            return  redirect(url)
        else:
            url = 'registerInvestor/'
            messages.error(self.request, "Passwords must match.")
            return  redirect(url)

def logInUser(request):
    storage = []
    if request.method =='POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None :
                print("Autenticado")
                login(request, user)
                if user.isEnterprise == True:
                    url = '/catalog/enterpriseView/' + user.idUser
                    return  redirect(url)
                else:
                    url = '/catalog/investorView/' + user.idUser
                    return  redirect(url)
                
            else:
                messages.error(request, "Invalid login, username doen't exist or password doesn't match.")
        else:
            messages.error(request, "Invalid login, username doen't exist or password doesn't match.")
    storage = get_messages(request)
    return render(request, 'catalog/logIn.html' ,context={'form':LogInForm, 'messages': storage})

def logOutUser(request):
    logout(request)
    return redirect('/')


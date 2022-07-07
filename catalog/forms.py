
from django import forms
from django.forms import ModelForm, TextInput, PasswordInput
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from catalog.models import Enterprise, Investor, Market, User, Stocks

#search about forms and login and register

class LogInForm(ModelForm):
    class Meta:
        model = User
        help_texts = {
            'username': None,
        }
        fields = ['username', 'password']
        widgets = {
            'username': TextInput(attrs={
                'class': "form-control", 
                'style': 'width: 400px; height: 50px; text-align: center;',
                'placeholder': 'User name'
                }),
            'password': PasswordInput(attrs={
                'class': "form-control", 
                'style': 'width: 400px; height: 50px; text-align: center;',
                'placeholder': 'Password'
                })
        }

class EnterpriseSignUpForm(UserCreationForm):
    username = forms.Field(required=True,widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'User name'}))
    password1 = forms.Field(required=True,widget=forms.PasswordInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Password'}))
    password2 = forms.Field(required=True,widget=forms.PasswordInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Confirm password'}))
    Name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Full name'}))
    Address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Address'}))
    Phone = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Phone Number'}))
    wallet = forms.DecimalField(max_digits=15,decimal_places=2,required=True,widget=forms.NumberInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Company\'s wallet'}))
    interest = forms.DecimalField(max_digits=15,decimal_places=2, widget=forms.NumberInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Company\'s interest'}))

    class Meta(UserCreationForm.Meta):
        model = User
        help_texts = {
            'username': None,
        }

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.isEnterprise = True
        user.save()
        enterprise = Enterprise.objects.create(user=user)
        enterprise.companyName = self.cleaned_data.get('Name')
        enterprise.companyAddress = self.cleaned_data.get('Address')
        enterprise.phoneNumber = self.cleaned_data.get('Phone')
        enterprise.wallet = self.cleaned_data.get('wallet')
        enterprise.interest = self.cleaned_data.get('interest')
        enterprise.save()
        return user

""" password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            ) """


class InvestorSignUpForm(UserCreationForm):
    username = forms.Field(required=True,widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'User name'}))
    password1 = forms.Field(required=True,widget=forms.PasswordInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Password'}))
    password2 = forms.Field(required=True,widget=forms.PasswordInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Confirm password'}))
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Full name'}))
    IDNum = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Persons ID'}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Address'}))
    phoneNumber = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'style':'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Phone Number'}))
    wallet = forms.DecimalField(max_digits=15,decimal_places=2, widget=forms.NumberInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Investor\'s wallet'}))

    class Meta(UserCreationForm.Meta):
        model = User
        model = User
        help_texts = {
            'username': None,
        }
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.isInvestor = True
        user.save()
        investor = Investor.objects.create(user=user)
        investor.name = self.cleaned_data.get('name')
        investor.IDNum = self.cleaned_data.get('IDNum')
        investor.address = self.cleaned_data.get('address')
        investor.phoneNumber = self.cleaned_data.get('phoneNumber')
        investor.wallet = self.cleaned_data.get('wallet')
        investor.save()
        return user


class BuyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BuyForm, self).__init__(*args, **kwargs)
        market = set(Market.objects.all())
        marketChoices = []
        #marketIdChoices = []
        for mar in market:
            marketChoices.append(mar.idEnterprise.companyName)
            #marketIdChoices.append(mar.idEnterprise.user.idUser)
        #Delete duplicated elems
        marketChoicesFinal = []
        flag = False
        for marF in marketChoices:
            flag= False
            for x in marketChoicesFinal:
                if (marF==x):
                    flag=True
                else:
                    flag=False 
            if flag==False:
                marketChoicesFinal.append(marF)

        self.fields['enterpriseName'].choices = zip(marketChoicesFinal, marketChoicesFinal)
    
    def clean_cuantity(self):
        data = self.cleaned_data['cuantity']
        if data <= 0.0:
            raise forms.ValidationError('Amount must be superior to 0') 
        return data

    enterpriseName = forms.ChoiceField()
    cuantity = forms.DecimalField(max_digits=6, decimal_places=0)


class SellForm(forms.Form):

    def clean_price(self):
        data = self.cleaned_data['price']
        if data <= 0.0:
            raise forms.ValidationError('Price must be superior to 0') 
        return data
    
    enterprise = forms.CharField(max_length=50, empty_value="Write One", widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Enterprise'}))
    cuantity = forms.DecimalField(max_digits=6, decimal_places=0, widget=forms.NumberInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Cuantity'}))
    price = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class':'form-control', 'style': 'width: 400px; height: 50px; text-align: center;', 'placeholder': 'Price'}))

class EmitForm(forms.Form):
    def clean_cuantity(self):
        data = self.cleaned_data['amount']
        if data <= 0.0:
            raise forms.ValidationError('Amount must be superior to 0') 
        return data

    amount = forms.DecimalField(max_digits=6, decimal_places=0, widget=forms.NumberInput(attrs={'class':'form-control', 'style': 'width: 200px; height: 50px; text-align: center;', 'placeholder': 'Amount to emit'}))

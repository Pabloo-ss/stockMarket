from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
import uuid # Required for unique book instances
from django import forms
from django.contrib.auth.models import AbstractUser
from datetime import date

class User (AbstractUser):
    """Model representing an User"""
    idUser = models.CharField(primary_key=True, max_length=100, default=uuid.uuid4)
    isInvestor = models.BooleanField(default=False)
    isEnterprise = models.BooleanField(default=False)

    class Meta:
        ordering = ['idUser']

    def _str_(self):
        """String for representing the Model object."""
        return f'{self.userName}'

class Enterprise(models.Model):
    """Model representing an Enterprise""" 
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    companyName = models.CharField(max_length=100, unique=True, null=True, blank=True)
    companyAddress = models.CharField(max_length=100, null=True, blank=True)
    phoneNumber = models.CharField(max_length=100, null=True, blank=True)
    wallet = models.DecimalField(max_digits=15,decimal_places=2, null=True, blank=True)
    interest = models.DecimalField(max_digits=6,decimal_places=2, null=True, blank=True)


    def get_absolute_url(self):
        """Returns the url to access a particular enterprise instance."""
        return reverse('enterprise-detail', args=[str(self.id)])

    def _str_(self):
        """String for representing the Model object."""
        return f'{self.name}'


class Investor(models.Model):
    """Model representing an Investor"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    IDNum = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phoneNumber = models.CharField(max_length=100, null=True, blank=True)
    wallet = models.DecimalField(max_digits=15,decimal_places=2, null=True, blank=True)


    def get_absolute_url(self):
        """Returns the url to access a particular enterprise instance."""
        return reverse('investor-detail', args=[str(self.id)])

    def _str_(self):
        """String for representing the Model object."""
        return f'{self.name}'

class Stocks(models.Model):
    """Model representing Stocks"""
    idUser = models.ForeignKey(User, on_delete=models.CASCADE)
    idEnterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    cuantity = models.DecimalField(max_digits=10,decimal_places=0, null=True, blank=True)

    class Meta:
        unique_together = (("idUser", "idEnterprise"),)

    def _str_(self):
        """String for representing the Model object."""
        return f'{self.id_user + self.id_enterprise + self.cuantity}'

class Market(models.Model):
    """Model representing Market offer"""
    idUser = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    idEnterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, null=False, blank=False)
    cuantity = models.DecimalField(max_digits=10,decimal_places=0, null=True, blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)

    def _str_(self):
        """String for representing the Model object."""
        return f'{self.id_enterprise + self.cuantity + self.cuantity}'
        

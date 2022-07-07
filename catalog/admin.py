from django.contrib import admin
from .models import Enterprise, Investor, User, Stocks, Market

@admin.register(User)
class UserAdmin(admin.ModelAdmin): pass

@admin.register(Enterprise)
class UserAdmin(admin.ModelAdmin): pass

@admin.register(Investor)
class UserAdmin(admin.ModelAdmin): pass

@admin.register(Stocks)
class UserAdmin(admin.ModelAdmin): pass

@admin.register(Market)
class UserAdmin(admin.ModelAdmin): pass

# Register your models here.

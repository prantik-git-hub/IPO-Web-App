from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib import admin

from .models import IPO, Company, Document

class MyAdminSite(AdminSite):
    site_header = "Bluestock Fintech Admin"
    site_title = "Bluestock Admin Portal"
    index_title = "Welcome to Bluestock Fintech Admin"

admin_site = MyAdminSite(name='myadmin')

# ✅ Register default auth models
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

# ✅ Register your app models

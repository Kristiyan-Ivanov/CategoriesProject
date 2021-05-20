from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category


class CustomModelAdmin(MPTTModelAdmin):
    exclude = ('slug',)


admin.site.register(Category, CustomModelAdmin)

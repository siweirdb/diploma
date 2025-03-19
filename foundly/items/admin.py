from django.contrib import admin
from .models import Category, Subcategory, Subsubcategory, Item, ItemPhoto

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Subsubcategory)
admin.site.register(Item)
admin.site.register(ItemPhoto)

from django.contrib import admin
from items.models import VerificationCode, Category, Subcategory, Subsubcategory, Item, ItemPhoto, User

admin.site.register(VerificationCode)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Subsubcategory)
admin.site.register(Item)
admin.site.register(ItemPhoto)
admin.site.register(User)

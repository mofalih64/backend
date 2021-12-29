from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from commerce.models import Product, Order, Item, Category, Vendor, Wish_list, Type


class ProductAdmin(admin.ModelAdmin):

    list_display = ('id', 'name','image', 'description', 'price', 'discounted_price')
    list_filter = ('category', 'vendor','type')
    search_fields = ('name', 'description','price', 'discounted_price','type')

admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Item)
admin.site.register(Wish_list)


admin.site.register(Category)
admin.site.register(Vendor)
admin.site.register(Type)



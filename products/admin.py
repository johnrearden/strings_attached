from django.contrib import admin
from .models import Product, Category, SpecialOffer, ProductAssociation


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'category', 'price', 'image',
                    'stock_level', 'reorder_threshold', 'product_owner',
                    'audio_clip', 'description',)
    list_editable = ('name', 'category', 'price', 'image', 'audio_clip',
                     'stock_level', 'reorder_threshold', 'product_owner',
                     'description',)

    ordering = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'friendly_name',)
    list_editable = ('friendly_name',)


class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'reduced_price',
                    'start_date', 'end_date',)
    list_editable = ('reduced_price',
                     'start_date', 'end_date',)


class ProductAssociationAdmin(admin.ModelAdmin):
    list_display = ('base_product', 'associated_product',)
    list_editable = ('associated_product',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SpecialOffer, SpecialOfferAdmin)
admin.site.register(ProductAssociation, ProductAssociationAdmin)

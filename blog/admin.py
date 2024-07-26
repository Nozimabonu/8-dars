from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from blog.models import Product, Image, Attribute, Customer, AttributeValue, ProductAttribute, User

# Register your models here.


# admin.site.register(Product)
admin.site.register(Image)
admin.site.register(Attribute)
# admin.site.register(Customer)
admin.site.register(AttributeValue)
admin.site.register(ProductAttribute)
admin.site.register(User)


# admin.site.register(admin.CustomerAdmin)


@admin.register(Product)
class Product(admin.ModelAdmin):
    List_display = ("name", 'price', 'slug')
    # prepopulated_fields = {'slug': ('name',)}


@admin.register(Customer)
class CustomerModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("name", "email", "phone")

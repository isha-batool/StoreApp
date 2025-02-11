from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models
from tags.models import TaggedItem 

class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','unit_price','inventory_status', 'collection']
    list_editable = ['unit_price']
    list_per_page = 5
    list_select_related = ['collection']
    list_filter = ['collection','last_update']
    actions = ['clear_inventory']
    search_fields = ['title','description']
    inlines = [TagInline]


    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    
    @admin.action(description = 'Clear Inventory')
    def clear_inventory(self,request,queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfuly updated'
        )

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','membership']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['first_name','last_name']
    search_fields = ['first_name','last_name']

class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']
    list_display = ['id','placed_at','customer']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id':str(collection.id)
                })
            )
        return format_html('<a href="{}">{}</a>',url,collection.products_count)
    


    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count = Count('product')
        )
    

#admin.site.register(models.Product, ProductAdmin)

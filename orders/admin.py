from django.contrib import admin
from .models import Order, OrderDetails, OrderNotification
import csv
import datetime
from django.http import HttpResponse


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # write the header row
    writer.writerow([field.verbose_name for field in fields])
    # write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'


class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'specification_of_product', 'address_of_delivery', 'created', 'modified', 'active', 'approved', 'paid']
    list_editable = ['active', 'approved', 'paid']
    actions = [export_to_csv]
# admin.site.register(OrderDetails, OrderDetailsAdmin)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'user', 'price', 'product', 'quantity']
    list_filter = ['product', 'quantity', 'created']
    actions = [export_to_csv]
# admin.site.register(Order, OrderItemAdmin)


class OrderNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created']
# admin.site.register(OrderNotification, OrderNotificationAdmin)

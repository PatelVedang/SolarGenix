from django.contrib import admin
from .models import Target, Tool, Subscription, SubscriptionHistory, TargetLog, Order

# This is a Django admin class that adds bulk actions to soft delete and recover selected items.
class BulkSelectedDelete(admin.ModelAdmin):
    actions = ['soft_delete_selected', 'soft_delete_recover_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def delete_selected(self, request, queryset):
        queryset.update(is_deleted=True)
    
    def soft_delete_selected(self, request, queryset):
        queryset.update(is_deleted=True)
    
    def soft_delete_recover_selected(self, request, queryset):
        queryset.update(is_deleted=False)


# Register your models here.
class TargetAdmin(BulkSelectedDelete):
    readonly_fields = ('id','retry')
    list_display = [
        'id', 'ip','get_full_name','status', 'tool', 'is_deleted','order_id', 'scan_time'
    ]
    search_fields = ('ip','id')

    def get_full_name(self, obj):
        """
        This function returns the full name of an object's "scan_by" attribute by concatenating the
        first and last name.
        
        :param obj: The "obj" parameter is an instance of a model object that is passed to the
        "get_full_name" method as an argument. The method then uses the attributes of this object to
        construct and return a full name string
        :return: a string that concatenates the first name and last name of the object's `scan_by`
        attribute, separated by a space.
        """
        return f'{obj.scan_by.first_name} {obj.scan_by.last_name}'
    get_full_name.short_description = 'Scan By'

class OrderAdmin(BulkSelectedDelete):
    readonly_fields = ('id','retry')
    search_fields = ('target_ip','id')
    list_display = [
        'id','target_ip', 'status', 'get_full_name', 'get_targets_count', 'is_deleted'
    ]

    def get_full_name(self, obj):
        """
        This function returns the full name of an object's "scan_by" attribute by concatenating the
        first and last name.
        
        :param obj: The "obj" parameter is an instance of a model object that is passed to the
        "get_full_name" method as an argument. The method then uses the attributes of this object to
        construct and return a full name string
        :return: a string that concatenates the first name and last name of the object's `scan_by`
        attribute, separated by a space.
        """
        return f'{obj.client.first_name} {obj.client.last_name}'
    get_full_name.short_description = 'Client'
    
    def get_targets_count(self, obj):
        """
        This function returns the count of targets associated with a given order object.
        
        :param obj: The "obj" parameter is an instance of an Order object. The function is using this
        object to filter the related Target objects and count them
        :return: a string that represents the number of Target objects that are associated with the
        input object (obj).
        """
        targets = Target.objects.filter(order=obj).count()
        return f'{targets}'
    get_targets_count.short_description = 'Total Targets'



class ToolAdmin(BulkSelectedDelete):
    readonly_fields = ('id',)
    list_display = ['id','tool_name', 'tool_cmd', 'is_deleted']

class SubscriptionHistoryAdmin(admin.ModelAdmin):
     list_display = [
        'buyer', 'tools_ids', 'start_date', 'end_date', 'status'
    ]


class TargetLogsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'target', 'get_target_id','get_full_name', 'action', 'created_at'
    ]

    def get_full_name(self, obj):
        """
        This function returns the full name of an object's "scan_by" attribute by concatenating the
        first and last name.
        
        :param obj: The "obj" parameter is an instance of a model object that is passed to the
        "get_full_name" method as an argument. The method then uses the attributes of this object to
        construct and return a full name string
        :return: a string that concatenates the first name and last name of the object's `scan_by`
        attribute, separated by a space.
        """
        return f'{obj.target.scan_by.first_name} {obj.target.scan_by.last_name}'
    get_full_name.short_description = 'User'

    def get_target_id(self, obj):
        """
        This function returns the ID of the target object.
        
        :param obj: The "obj" parameter is an object that is passed as an argument to the function. The
        function is expected to extract the "id" attribute of the "target" attribute of the object and
        return it
        :return: The function `get_target_id` is returning the `id` attribute of the `target` object of
        the input `obj`.
        """
        return obj.target.id
    get_target_id.short_description = 'Target ID'

admin.site.register(Target, TargetAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(Subscription)
admin.site.register(SubscriptionHistory, SubscriptionHistoryAdmin)
admin.site.register(TargetLog, TargetLogsAdmin)
admin.site.register(Order, OrderAdmin)
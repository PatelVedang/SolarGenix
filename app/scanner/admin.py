from django.contrib import admin
from .models import Target, Tool, Subscription, SubscriptionHistory, TargetLog, Order

# This is a Django admin class that adds bulk actions to soft delete and recover selected items.
class BulkSelect(admin.ModelAdmin):
    actions = ['soft_delete', 'soft_delete_recover', 'hard_delete', 'clone_selected']
    
    def get_actions(self, request):
        """
        This function removes the "delete_selected" action from the list of actions returned by the
        parent class.
        
        :param request: The `request` parameter is an object that represents the HTTP request made by
        the user. It contains information such as the HTTP method used (GET, POST, etc.), the URL being
        accessed, any query parameters, and any data submitted in the request body. In this specific
        code snippet, the `
        :return: The modified `actions` dictionary with the `'delete_selected'` key removed.
        """
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def delete_selected(self, request, queryset):
        """
        This function updates the "is_deleted" field of the selected objects in the queryset to True.
        
        :param request: The request object represents the current HTTP request that the user has made.
        It contains information about the user's request, such as the URL, headers, and any data that
        was submitted with the request
        :param queryset: `queryset` is a set of objects that have been selected by the user in the
        Django admin interface. It is a collection of model instances that match the selected items in
        the list view. In this case, the `update()` method is called on the queryset to set the
        `is_deleted`
        """
        queryset.update(is_deleted=True)

    def soft_delete(self, request, queryset):
        """
        This function updates the "is_deleted" field of the objects in the given queryset to True,
        effectively soft deleting them.
        
        :param request: The request object represents the current HTTP request that was made by the
        user. It contains information about the user, the requested URL, any submitted data, and other
        metadata related to the request
        :param queryset: The queryset parameter is a set of objects that have been selected for a
        particular operation. In this case, the objects are being marked as deleted by setting the
        "is_deleted" attribute to True
        """
        queryset.update(is_deleted=True)

    def hard_delete(self, request, queryset):
        """
        This function performs a hard delete operation on the queryset passed as an argument.
        
        :param request: The request parameter is an HttpRequest object that represents the current
        request made by the user. It contains information about the user's request, such as the HTTP
        method used, the URL requested, and any data submitted in the request. In this case, it is being
        passed to the hard_delete method as an
        :param queryset: The queryset parameter is a collection of objects that match a certain set of
        criteria. In this case, it is a collection of objects that the user wants to delete. The
        queryset is passed as an argument to the delete() method, which deletes all the objects in the
        queryset from the database
        """
        queryset.delete()
    
    def soft_delete_recover(self, request, queryset):
        """
        This function updates the "is_deleted" field of the selected queryset to False, effectively
        recovering any soft-deleted items.
        
        :param request: The request object represents the current HTTP request that was sent by the
        client to the server. It contains information about the request, such as the HTTP method used
        (e.g. GET, POST), the headers, the user agent, and any data that was sent in the request body
        :param queryset: `queryset` is a set of objects that have been selected for a particular
        operation. In this case, it is a set of objects that have been marked as deleted and need to be
        recovered by setting their `is_deleted` attribute to `False`. The `update()` method is used to
        update
        """
        queryset.update(is_deleted=False)
    
    def clone_selected(self, request, queryset):
        """
        This function clones selected objects by creating new instances with cleared primary keys.
        
        :param request: The request object represents the current HTTP request that was sent to the
        server. It contains information about the user making the request, the requested URL, any data
        submitted in the request, and more
        :param queryset: `queryset` is a collection of objects that have been selected by the user in
        the Django admin interface. It is a QuerySet object that represents a set of database records
        that match certain criteria. In this case, the queryset contains the objects that the user wants
        to clone. The `clone_selected
        """
        for obj in queryset:
            obj.pk = None  # Clear the primary key to create a new instance
            obj.save()
    
    soft_delete.short_description = "Soft delete selected %(verbose_name_plural)s"
    hard_delete.short_description = "Hard delete selected %(verbose_name_plural)s"
    soft_delete_recover.short_description = "Recover soft deleted selected %(verbose_name_plural)s"
    clone_selected.short_description = "Clone selected %(verbose_name_plural)s"


# Register your models here.
class TargetAdmin(BulkSelect):
    readonly_fields = ('id','retry')
    list_display = [
        'id', 'ip','get_full_name','status', 'tool', 'is_deleted','order_id', 'scan_time'
    ]
    search_fields = ('ip','id', 'scan_by__first_name', 'scan_by__last_name', 'tool__tool_name')

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

class OrderAdmin(BulkSelect):
    readonly_fields = ('id','retry')
    search_fields = ('target_ip','id', 'client__first_name', 'client__last_name')
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
        if obj.client:
            return f'{obj.client.first_name} {obj.client.last_name}'
        return None
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



class ToolAdmin(BulkSelect):
    readonly_fields = ('id',)
    list_display = ['id','tool_name', 'tool_cmd', 'is_deleted', 'subscription', 'py_tool']
    actions = ['make_it_as_staff_tool'] + BulkSelect.actions
    search_fields = ('id', 'subscription__plan_type', 'tool_name', 'tool_cmd')

    def make_it_as_staff_tool(self, request, queryset):
        """
        This function updates the subscription field of the selected query set to 1.
        
        :param request: The request parameter is an object that represents the HTTP request made by the
        user. It contains information such as the user's session, the HTTP method used (GET, POST,
        etc.), and any data submitted in the request. In this specific function, the request parameter
        is not used, but it is
        :param queryset: `queryset` is a set of objects that have been selected by the user in the
        Django admin interface. In this case, the `update()` method is being called on the queryset to
        set the `subscription` field of all selected objects to 1
        """
        queryset.update(subscription=2)

    def get_subscription(self, obj):
        """
        This function returns the plan type of a subscription object.
        
        :param obj: The "obj" parameter is an instance of a model object that has a "subscription"
        attribute. The method is using this attribute to retrieve the "plan_type" of the subscription
        and returning it as a string
        :return: a string that represents the plan type of the subscription object passed as an
        argument.
        """
        return f"{obj.subscription.plan_type}"
    
    get_subscription.short_description = 'Subscription'
    make_it_as_staff_tool.short_description = 'Make selected %(verbose_name_plural)s as staff only'

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

class SubscriptionAdmin(BulkSelect):
    list_display = [
        'id','plan_type', 'mail_scan_result'
    ]
    search_fields = ('id','plan_type')

admin.site.register(Target, TargetAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SubscriptionHistory, SubscriptionHistoryAdmin)
admin.site.register(TargetLog, TargetLogsAdmin)
admin.site.register(Order, OrderAdmin)
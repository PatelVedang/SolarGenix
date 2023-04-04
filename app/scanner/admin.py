from django.contrib import admin
from .models import Target, Tool, Subscription, SubscriptionHistory, TargetLog, Order

class BulkSelectedDelete(admin.ModelAdmin):
    actions = ['soft_delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def delete_selected(self, request, queryset):
        queryset.update(is_deleted=True)
    
    def soft_delete_selected(self, request, queryset):
        queryset.update(is_deleted=True)


# Register your models here.
class TargetAdmin(BulkSelectedDelete):
    readonly_fields = ('id','retry')
    list_display = [
        'id', 'ip','get_full_name','status', 'tool', 'is_deleted','order_id'
    ]
    search_fields = ('ip','id')

    def get_full_name(self, obj):
        return f'{obj.scan_by.first_name} {obj.scan_by.last_name}'
    get_full_name.short_description = 'Scan By'

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('id','retry')
    search_fields = ('target_ip','id')
    list_display = [
        'id','target_ip', 'status', 'get_full_name', 'get_targets_count', 'is_deleted'
    ]

    def get_full_name(self, obj):
        return f'{obj.client.first_name} {obj.client.last_name}'
    get_full_name.short_description = 'Client'
    
    def get_targets_count(self, obj):
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
        return f'{obj.target.scan_by.first_name} {obj.target.scan_by.last_name}'
    get_full_name.short_description = 'User'

    def get_target_id(self, obj):
        return obj.target.id
    get_target_id.short_description = 'Target ID'

admin.site.register(Target, TargetAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(Subscription)
admin.site.register(SubscriptionHistory, SubscriptionHistoryAdmin)
admin.site.register(TargetLog, TargetLogsAdmin)
admin.site.register(Order, OrderAdmin)
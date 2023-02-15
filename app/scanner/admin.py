from django.contrib import admin
from .models import Target, Tool, Subscription, SubscriptionHistory, TargetLog

# Register your models here.
class TargetAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id', 'ip','get_full_name','status', 'tool'
    ]
    search_fields = ('ip','id')

    def get_full_name(self, obj):
        return f'{obj.scan_by.first_name} {obj.scan_by.last_name}'
    get_full_name.short_description = 'Scan By'

class ToolAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

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
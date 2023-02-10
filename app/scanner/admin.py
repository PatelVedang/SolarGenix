from django.contrib import admin
from .models import Target, Tool, Subscription, SubscriptionHistory

# Register your models here.
class MachineAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id', 'ip','scan_by','status', 'tool'
    ]
    search_fields = ('ip','id')
class ToolAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

class SubscriptionHistoryAdmin(admin.ModelAdmin):
     list_display = [
        'buyer', 'tools_ids', 'start_date', 'end_date', 'status'
    ]  
admin.site.register(Target, MachineAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(Subscription)
admin.site.register(SubscriptionHistory, SubscriptionHistoryAdmin)
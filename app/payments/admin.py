from django.contrib import admin
from .models import PaymentHistory
# Register your models here.
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name','stripe_subscription_id','price_id','status','created_at','current_period_start','current_period_end','ip_limit'
    ]

    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

admin.site.register(PaymentHistory, PaymentHistoryAdmin)
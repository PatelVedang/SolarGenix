from django.contrib import admin
from .models import Machine

# Register your models here.
class MachineAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Machine, MachineAdmin)
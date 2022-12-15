from django.contrib import admin
from .models import Machine, Tool

# Register your models here.
class MachineAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
class ToolAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Tool, ToolAdmin)
from django.contrib import admin
from blog_app.models import ContactUs
from blog_app.admin.base_admin import BaseAdmin

@admin.register(ContactUs)
class ContactUsAdmin(BaseAdmin):
    list_display = ('name', 'email', 'created_at', 'short_message')
    list_filter = ('created_at', 'email')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')

    def short_message(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    short_message.short_description = 'Message Snippet'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
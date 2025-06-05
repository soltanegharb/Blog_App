from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from blog_app.admin.base_admin import BaseAdmin
from blog_app.models import CustomUser
from blog_app.forms.user import UserRegistration, UserProfile

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, BaseAdmin):
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'is_active',
        'date_joined',
        'post_count'
    )
    list_filter = BaseUserAdmin.list_filter + ('date_joined',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Profile', {'fields': ('bio', 'profile_image')}),
    )
    
    readonly_fields = BaseUserAdmin.readonly_fields + ('post_count',)

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Posts'

    # actions = ['activate_users', 'deactivate_users']

    # def activate_users(self, request, queryset):
    #     queryset.update(is_active=True)
    #     self.message_user(request, "Selected users have been activated.")
    # activate_users.short_description = "Activate selected users"

    # def deactivate_users(self, request, queryset):
    #     queryset.update(is_active=False)
    #     self.message_user(request, "Selected users have been deactivated.")
    # deactivate_users.short_description = "Deactivate selected users"
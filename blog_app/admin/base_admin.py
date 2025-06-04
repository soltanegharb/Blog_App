from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):

    list_display = tuple()
    list_filter = tuple()
    search_fields = tuple()
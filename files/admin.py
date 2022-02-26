from django.contrib import admin

from files.models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'posted_at')
    list_filter = ('author', 'posted_at')
    search_fields = ('title', 'author')
    order_by = ('-posted_at',)

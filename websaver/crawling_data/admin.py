from django.contrib import admin
from .models import Notice

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('num', 'title', 'category', 'created_at', 'saved_at', 'updated_at', 'status')
    list_display_links = ('num', 'title')
    list_filter = ('category', 'status')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    list_per_page = 25

# Register your models here.
admin.site.register(Notice, NoticeAdmin)
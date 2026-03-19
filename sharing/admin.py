from django.contrib import admin
from .models import ShareHistory

@admin.register(ShareHistory)
class ShareHistoryAdmin(admin.ModelAdmin):
    list_display = ('resume', 'method', 'recipient', 'timestamp')
    search_fields = ('recipient',)
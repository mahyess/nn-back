from django.contrib import admin
from .models import Community, CommunityRequest

# readonly_fields = ['password', 'last_login', 'date_joined', 'email', 'online']


class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_subs', 'timestamp', 'is_private']


class CommunityRequestAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityRequest, CommunityRequestAdmin)

from django.contrib import admin

from .models import HashTag
from .models.user import User, Gender

from .models.deletedPosts import DeletedPost
from .models.legal import PrivacyPolicy, StoragePolicy, Term


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "online", "date_joined", "last_login"]
    readonly_fields = ["uid", "email", "last_login", "date_joined", "online"]
    exclude = ["password"]


@admin.register(HashTag)
class RecentMessageAdmin(admin.ModelAdmin):
    list_display = ["title"]


admin.site.register(User, UserAdmin)
admin.site.register(Gender)
# admin.site.register(Message)
# admin.site.register(GroupMessage)
admin.site.register(DeletedPost)
# admin.site.register(MessageUserGroup)
# admin.site.register(RecentMessage, RecentMessageAdmin)
admin.site.register(Term)
admin.site.register(PrivacyPolicy)
admin.site.register(StoragePolicy)
# admin.site.register(MessageUsersGroup)

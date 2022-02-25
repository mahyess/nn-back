from django.contrib import admin
from .models import Profile, Friend, FriendRequest, BlockedUser, CelebVerification, AuditLogs

myModels = [Profile, Friend,
            FriendRequest, BlockedUser, CelebVerification, AuditLogs]
admin.site.register(myModels)

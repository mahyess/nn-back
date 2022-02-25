from django.contrib import admin
from .models import Attachment, Post, Comment


# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "total_likes", "deleted", "user", "community")
    list_filter = (
        "user",
        "community",
        "deleted",
    )

    def get_queryset(self, request):
        """Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view."""

        # Default: qs = self.model._default_manager.get_query_set()
        qs = self.model._default_manager.all_with_deleted()

        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = (
            self.ordering or ()
        )  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    queryset = get_queryset


class PostInline(admin.TabularInline):
    model = Post.attachments.through


class AttachmentAdmin(admin.ModelAdmin):
    inlines = [PostInline]
    list_display = (
        "id",
        "__str__",
    )
    list_filter = (
        # "post__user__username",
        "category",
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Attachment, AttachmentAdmin)

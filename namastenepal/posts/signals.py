import re

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from namastenepal.usermodule.models import AuditLogs
from .models import Post, Comment


@receiver(post_save, sender=Post)
def create_user_post_log(**kwargs):
    """
    create log on post save
    :param kwargs:
    :return:
    """
    instance = kwargs.pop("instance", None)
    created = kwargs.pop("created", None)

    if created:
        task = AuditLogs.objects.create(user=instance.user)
        task.action = f"created a post on {instance.community.name if instance.community else 'their profile'}"
        task.slug = instance.slug
        task.save()


@receiver(post_save, sender=Comment)
def create_user_comment_log(**kwargs):
    """
    create log on comment save
    :param kwargs:
    :return:
    """
    instance = kwargs.pop("instance", None)
    created = kwargs.pop("created", None)
    if created:
        if instance.parent:
            task_action = "replied on a comment"
        else:
            task_action = "commented on a post"
        AuditLogs.objects.create(
            user=instance.user, slug=instance.post.slug, action=task_action
        )


# from django.db import transaction
#
#
# # def on_transaction_commit(func):
# #     def inner(*args, **kwargs):
# #         transaction.on_commit(lambda: func(*args, **kwargs))
# #
# #     return inner
#
#
# # @on_transaction_commit
# @receiver(post_save, sender=Comment)
# def link_mentions_to_comment(**kwargs):
#     """
#     create log on comment save
#     :param kwargs:
#     :return:
#     """
#     comment_instance = kwargs.pop("instance", None)
#     created = kwargs.pop("created", None)
#
#     if created:
#         mentions = re.findall(r"@(\S+)", comment_instance.comment)
#         print(mentions, type(mentions))
#         with transaction.atomic():
#             transaction.on_commit(
#                 comment_instance.mentions.set(
#                     list(get_user_model().objects.filter(username__in=mentions))
#                 )
#             )
#         # comment_instance.save()

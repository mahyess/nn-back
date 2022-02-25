from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from namastenepal.points.pointSystem import PointSystem
from namastenepal.posts.models import Post, Comment
from namastenepal.usermodule.models import FriendRequest
from .models import (
    PostNotification,
    Notification,
    CommentNotification,
    FriendNotification,
)


def create_comment_notification(comment, sender_id, receiver_id, action, category):
    """
    :param comment: comment instance
    :param sender_id: sender user id
    :param receiver_id: receiver user id
    :param action: str of message "comment/reply/request/mention"
    :param category: "comment/reply/request/mention"
    :return: ``CommentNotification`` instance
    """
    return CommentNotification.objects.create(
        notification=Notification.objects.create(
            user_id=receiver_id,
            sender_id=sender_id,
            action=action,
            category=Notification.COMMENT,
        ),
        comment=comment,
        category=category,
    )


@receiver(post_save, sender=Post.tags.through)
def notification_on_post_tag(**kwargs):
    post = kwargs.pop("instance")
    action = kwargs.pop("action", None)
    pk_set = kwargs.pop("pk_set", None)

    for pk in pk_set:
        if not post.user.id == pk:  # self interaction doesnt trigger
            if action == "post_add":
                notification = Notification.objects.filter(
                    user_id=pk,
                    sender=post.user,
                    post_notification__post=post,
                    post_notification__category=PostNotification.TAG,
                )
                if notification.exists():
                    notification.update(action="tagged you on the post.")
                else:
                    PostNotification.objects.create(
                        notification=Notification.objects.create(
                            user_id=pk,
                            sender=post.user,
                            action="tagged you on the post.",
                            category=Notification.POST,
                        ),
                        post=post,
                        category=PostNotification.TAG,
                    )


@receiver(m2m_changed, sender=Post.likes.through)
def notification_and_points_on_like(**kwargs):
    """
    on like, create notification for like and manage points for user
    :param kwargs:
    :return:
    """
    post = kwargs.pop("instance", None)
    action = kwargs.pop("action", None)
    pk_set = kwargs.pop("pk_set", None)

    ps = PointSystem()

    for pk in pk_set:
        if not post.user.id == pk:  # self interaction doesnt trigger
            if action == "post_add":
                notification = Notification.objects.filter(
                    user=post.user,
                    sender_id=pk,
                    post_notification__post=post,
                    post_notification__category=PostNotification.LIKE,
                )
                if notification.exists():
                    notification.update(action="added namaste on the post.")
                else:
                    PostNotification.objects.create(
                        notification=Notification.objects.create(
                            user=post.user,
                            sender_id=pk,
                            action="added namaste on the post.",
                            category=Notification.POST,
                        ),
                        post=post,
                        category=PostNotification.LIKE,
                    )

                # add point
                if post.community:
                    _ = ps.manage_points(_type="add_namaste", post=post)

            elif action == "post_remove":
                Notification.objects.update_or_create(
                    user=post.user,
                    sender_id=pk,
                    post_notification__post=post,
                    post_notification__category=PostNotification.LIKE,
                    defaults={"action": "removed namaste on the post."},
                )
                # remove point
                if post.community:
                    _ = ps.manage_points(_type="remove_namaste", post=post)


@receiver(post_save, sender=Comment)
def notification_on_comment(**kwargs):
    """
    on like, create notification for like and manage points for user
    :param kwargs:
    :return:
    """
    comment: Comment = kwargs.pop("instance", None)
    created = kwargs.pop("created", None)

    if created:
        # self interaction doesnt trigger
        if not comment.user.id == comment.post.user.id:
            create_comment_notification(
                comment=comment,
                sender_id=comment.user.id,
                receiver_id=comment.post.user.id,
                action="commented on your post.",
                category=CommentNotification.COMMENT,
            )
        if comment.parent and comment.approved:
            for receiving_user in comment.parent.discuss_group.exclude(
                id=comment.user.id
            ):
                create_comment_notification(
                    comment=comment,
                    sender_id=comment.user.id,
                    receiver_id=receiving_user.id,
                    action="added a reply on your chalfal.",
                    category=CommentNotification.REPLY,
                )


@receiver(m2m_changed, sender=Comment.up_votes.through)
def notification_and_points_on_up_vote(**kwargs):
    comment = kwargs.pop("instance")
    pk_set = kwargs.pop("pk_set")
    action = kwargs.pop("action")

    ps = PointSystem()
    for pk in pk_set:
        if action == "post_add":
            notification = Notification.objects.filter(
                user=comment.user,
                sender_id=pk,
                comment_notification__comment=comment,
                comment_notification__category=CommentNotification.UPVOTE,
            )
            if notification.exists():
                notification.update(action="upvoted on a comment.")
            else:
                create_comment_notification(
                    comment=comment,
                    sender_id=pk,
                    receiver_id=comment.user.pk,
                    action="upvoted on your comment.",
                    category=CommentNotification.UPVOTE,
                )

            # add point
            if comment.post.community:
                _ = ps.manage_points(_type="vote_up", comment=comment)
        elif action == "post_remove":
            Notification.objects.update_or_create(
                user=comment.user,
                sender_id=pk,
                comment_notification__comment=comment,
                comment_notification__category=CommentNotification.UPVOTE,
                defaults={"action": "unupvoted on a comment."},
            )
            if comment.post.community:
                _ = ps.manage_points(_type="vote_down", comment=comment)


@receiver(m2m_changed, sender=Comment.down_votes.through)
def notification_and_points_on_down_vote(**kwargs):
    comment = kwargs.pop("instance")
    pk_set = kwargs.pop("pk_set")
    action = kwargs.pop("action")

    ps = PointSystem()
    for _ in pk_set:
        if action == "post_add":
            # add point
            if comment.post.community:
                _ = ps.manage_points(_type="vote_down", comment=comment)
        elif action == "post_remove":
            if comment.post.community:
                _ = ps.manage_points(_type="vote_up", comment=comment)


@receiver(m2m_changed, sender=Comment.mentions.through)
def notification_and_points_on_up_vote(**kwargs):
    comment = kwargs.pop("instance")
    pk_set = kwargs.pop("pk_set")
    action = kwargs.pop("action")

    for pk in pk_set:
        if action == "post_add":
            notification = Notification.objects.filter(
                user=comment.user,
                sender_id=pk,
                comment_notification__comment=comment,
                comment_notification__category=CommentNotification.MENTION,
            )
            if notification.exists():
                notification.update(action="mentioned on a comment.")
            else:
                create_comment_notification(
                    comment=comment,
                    sender_id=pk,
                    receiver_id=comment.user.pk,
                    action="mentioned on a comment.",
                    category=CommentNotification.MENTION,
                )


@receiver(post_save, sender=FriendRequest)
def notification_on_friend_request_accept(**kwargs):
    """
    on like, create notification for like and manage points for user
    :param kwargs:
    :return:
    """
    request: FriendRequest = kwargs.pop("instance", None)
    created = kwargs.pop("created", None)

    if (not created) and request.accepted:
        FriendNotification.objects.create(
            notification=Notification.objects.create(
                user=request.from_user,
                sender=request.to_user,
                action="accepted your friend request.",
                category=Notification.FRIEND,
            ),
            friend=request.to_user,
            category=FriendNotification.REQUEST_ACCEPT,
        )

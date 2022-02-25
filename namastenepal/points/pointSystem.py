from typing import Optional, Any

from .models import Point

# from namastenepal.community.models.Community import get_priority_choices
from namastenepal.community.models import Community


def multiplier(priority):
    if priority == Community.CRITICAL:
        return 3
    elif priority == Community.VERY_HIGH:
        return 2
    elif priority == Community.HIGH:
        return 1.5
    elif priority == Community.MEDIUM:
        return 1
    elif priority == Community.LOW:
        return 0.75
    else:
        return 1


class PointSystem(object):

    post: Optional[Any]
    comment: Optional[Any]

    def manage_points(self, _type, post=None, comment=None):
        # print(multiplier(post.community.priority))
        """Dispatch method"""
        # Get the method from 'self'. Default to a lambda.
        self.post = post if post else None
        self.comment = comment if comment else None
        method = getattr(self, _type, lambda: False)
        # Call the method as we return it
        return method()

    def add_namaste(self):
        pts, _ = Point.objects.get_or_create(user=self.post.user)
        pts.n_points = pts.n_points + 1 * multiplier(self.post.community.priority)
        pts.save()
        return True

    def vote_up(self):
        pts, _ = Point.objects.get_or_create(user=self.comment.user)
        pts.v_points = pts.v_points + 0.5 * multiplier(
            self.comment.post.community.priority
        )
        pts.save()
        return True

    def remove_namaste(self):
        pts, _ = Point.objects.get_or_create(user=self.post.user)
        pts.n_points = pts.n_points - 1 * multiplier(self.post.community.priority)
        pts.save()
        return True

    def vote_down(self):
        pts, _ = Point.objects.get_or_create(user=self.comment.user)
        pts.v_points = pts.v_points - 0.5 * multiplier(
            self.comment.post.community.priority
        )
        pts.save()
        return True

    def reported_post(self):
        pts, _ = Point.objects.get_or_create(user=self.post.user)
        pts.p_points = pts.p_points - 50 * multiplier(self.post.community.priority)
        pts.save()
        return True

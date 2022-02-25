from django.db import models
from django.utils import timezone


class SoftDeletableQS(models.QuerySet):
    """A queryset that allows soft-delete on its objects"""

    def delete(self, **kwargs):
        self.update(deleted=timezone.now(), **kwargs)
        print(self)

    def hard_delete(self, **kwargs):
        super().delete(**kwargs)


class SoftDeletableManager(models.Manager):
    """Manager that filters out soft-deleted objects"""

    def get_queryset(self):
        return super(SoftDeletableManager, self).get_queryset().filter(deleted__isnull=True)

    def all_with_deleted(self):
        return super(SoftDeletableManager, self).get_queryset()

    def deleted_set(self):
        return super(SoftDeletableManager, self).get_queryset().filter(deleted__isnull=False)

    def get(self, *args, **kwargs):
        ''' if a specific record was requested, return it even if it's deleted '''
        return self.all_with_deleted().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        ''' if pk was specified as a kwarg, return even if it's deleted '''
        if 'pk' in kwargs:
            return self.all_with_deleted().filter(*args, **kwargs)
        return self.get_queryset().filter(*args, **kwargs)

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "namastenepal.notifications"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import namastenepal.notifications.signals

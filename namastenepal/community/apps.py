from django.apps import AppConfig


class CommunityConfig(AppConfig):
    name = "namastenepal.community"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import namastenepal.community.signals

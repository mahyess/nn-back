from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "namastenepal.core"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import namastenepal.core.signals

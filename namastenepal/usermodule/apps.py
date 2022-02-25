from django.apps import AppConfig


class UsermoduleConfig(AppConfig):
    name = "namastenepal.usermodule"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import namastenepal.usermodule.signals

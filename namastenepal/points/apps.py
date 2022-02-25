from django.apps import AppConfig


class PointsConfig(AppConfig):
    name = "namastenepal.points"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import namastenepal.points.signals

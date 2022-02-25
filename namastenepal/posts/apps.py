from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = "namastenepal.posts"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import namastenepal.posts.signals

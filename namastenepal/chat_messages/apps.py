from django.apps import AppConfig


class ChatMessagesConfig(AppConfig):
    name = "namastenepal.chat_messages"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import namastenepal.chat_messages.signals

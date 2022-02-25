"""
firebase app
"""
from firebase_admin import credentials, initialize_app
from django.apps import AppConfig
from decouple import config


class FirebaseConfig(AppConfig):
    """Class representing Firebase application and its configuration."""

    name = "firebase"

    def ready(self):
        """Runs on Startup of Django project"""
        try:
            cred = credentials.Certificate(config("FIREBASE_ADMIN_SDK"))
            initialize_app(cred)
        except ImportError as import_error:
            raise ImportError(
                "Firebase Admin cannot be imported."
                "Are you sure it's installed in virtual environment?"
            ) from import_error

        # noinspection PyUnresolvedReferences
        import firebase.signals

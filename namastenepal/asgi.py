"""
ASGI entrypoint file for default channel layer.

Points to the channel layer configured as "default" so you can point
ASGI applications at "multichat.asgi:channel_layer" as their channel layer.
"""

import os
#
# from channels.asgi import get_channel_layer
from channels.routing import get_default_application
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "namastenepal.settings")
django.setup()
application = get_default_application()
# channel_layer = get_channel_layer()

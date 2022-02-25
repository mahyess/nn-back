"""
Base settings contain common settings for both local and production
Local settings are not pushed to git and are used for local settings
Since local settings are not in git, production settings are triggered in production
"""
from .base import *
try:
    # if DEBUG
    from .local import *
except ImportError:
    # if not DEBUG
    from .production import *

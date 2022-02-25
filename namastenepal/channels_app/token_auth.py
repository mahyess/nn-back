"""token auth"""
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser

from namastenepal.core.models import User
from rest_framework_jwt.utils import jwt_decode_handler


class TokenAuthMiddleware:
    """
    Token authorization middleware
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        try:
            query_string = dict(
                (x.split("=") for x in scope["query_string"].decode().split("&"))
            )
            # print(query_string)
            if "token" in query_string:
                token = query_string["token"]
                token = jwt_decode_handler(token)
                scope["user"] = User.objects.get(username=token.get("username"))
        except Exception as _:
            scope["user"] = AnonymousUser()
        return self.inner(scope)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))

import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from .models import Token
from .sdk import send_dry_run, send_to_token


@api_view(["POST"])
@login_required
def add_new_firebase_token(request):
    token = request.data.get("token")
    category = request.data.get("category").strip()[
        0
    ]  # whatever comes, get first letter

    user = request.user

    try:
        # dry run tests if the token is valid and working
        send_dry_run(token, {"test": "test"})
        # if success, continue
    except Exception as e:
        # if failed, returns whatever error that happened
        return Response(e, status=HTTP_400_BAD_REQUEST)

    Token.objects.create(user=user, token=token, category=category)

    return Response({"success": "Token added successfully."}, status=HTTP_201_CREATED)

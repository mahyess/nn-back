from django.conf import settings
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import pagination
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_200_OK, HTTP_401_UNAUTHORIZED
)

from namastenepal.core.models import User
from namastenepal.posts.models import Post
from .models import Community
from .serializers import (
    CommunitySerializer,
    IconSerializer,
    BackgroundImageSerializer,
    CommunityRequestSerializer
)


class PostPagination(pagination.PageNumberPagination):
    page_size = 5  # the no. of objects you want to send in one go


def offline(request):
    return HttpResponse("You are offline.")


@api_view(['POST'])
def join_community(request):
    community = request.data.get('samaj')
    if not community:
        msg = {"message": "Invalid Data."}
        return Response(msg, status=HTTP_400_BAD_REQUEST)

    try:
        _cmm = Community.objects.get(id=community)
    except Community.DoesNotExist:
        msg = {"message": "Samaj not found."}
        return Response(msg, status=HTTP_404_NOT_FOUND)

    _user: User = request.user
    if _cmm.is_private:
        msg = {"message": "Samaj is private."}
        return Response(msg, status=HTTP_404_NOT_FOUND)

    if _cmm.subscriber_gender:
        if not _user.gender == _cmm.subscriber_gender:
            msg = {"message": "Invalid Gender."}
            return Response(msg, status=HTTP_401_UNAUTHORIZED)

    if _user in _cmm.subscribers.all():
        msg = {"message": "You have already joined the Samaj."}
        return Response(msg, status=HTTP_400_BAD_REQUEST)
    else:
        _cmm.subscribers.add(_user)
        return Response({"message": "You have joined the Samaj."}, status=HTTP_200_OK)


@api_view(['POST'])
def leave_community(request):
    community = request.data.get('samaj')
    if not community:
        msg = {"samaj": "Samaj required."}
        return Response(msg, status=HTTP_400_BAD_REQUEST)

    try:
        _cmm = Community.objects.get(id=community)
    except Community.DoesNotExist:
        msg = {"message": "Samaj not found."}
        return Response(msg, status=HTTP_404_NOT_FOUND)

    _user: User = request.user
    if _user not in _cmm.subscribers.all():
        msg = {"message": "You have not joined the Samaj."}

        return Response(msg, status=HTTP_400_BAD_REQUEST)

    if _user in _cmm.admin.all():
        _cmm.admin.remove(_user)
    _cmm.subscribers.remove(_user)

    return Response({"message": "You have left the Samaj."}, status=HTTP_200_OK)


@api_view(['POST'])
def request_community(request):
    name = request.data.get('name')
    description = request.data.get('description')
    icon = request.data.get('icon')
    if icon == "" or icon == "null" or icon == "undefined" or not icon:
        icon = ""
    background = request.data.get('background')
    if background == "" or background == "null" or background == "undefined" or not background:
        background = ""
    requester = request.user
    # UserSerializer(data=request.user)

    serializer = CommunityRequestSerializer(data={
        "name": name,
        "description": description,
        "icon": icon,
        "background": background,
        "requester": requester.pk
    })
    if serializer.is_valid():
        serializer.save()
        return Response({"success": "samaj creation requested successfully."}, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def community_list(request):
    requesting_user: User = request.user
    community = Community.objects.filter(Q(subscriber_gender_id=requesting_user.gender.id) | Q(
        subscriber_gender__isnull=True), is_private=False).order_by('id')
    serializer = CommunitySerializer(community, many=True)
    return JsonResponse(serializer.data, safe=False)


# @api_view(['POST'])
# def updateCommunity(request, format=None):
#     slug = request.data.get('community')
#     cmm = Community.objects.get(slug=slug)
#     print(cmm)
#     serializer = UpdateCommunitySerializer(instance=cmm, data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         data = {"success": "Saved"}
#         return Response(serializer.data, status=HTTP_201_CREATED)
#     data = {"error": "not Saved"}
#     return Response(data, status=HTTP_400_BAD_REQUEST)

# End Community Related

# Community Post Related
#
# @api_view(['GET'])
# def get_community_details(request, id, slug):
#     try:
#         now_month = timezone.now().month
#
#         community = Community.objects.get(id=id, slug=slug)
#         active_users = Post.objects.filter(
#             community=community, timestamp__month=now_month) \
#                            .values('user_id', 'user__username', 'user__uid', 'user__profile__avatar',
#                                    'user__first_name', 'user__last_name') \
#                            .annotate(Count('id', distinct=True), Count('likes')).order_by('-id__count')[:3]
#
#         for value in active_users:
#             # value['user__profile__avatar'] = 'https://s3.us-east-2.amazonaws.com/namastenepal' +
#             settings.MEDIA_URL + value['user__profile__avatar']
#             value['user__profile__avatar'] = settings.MEDIA_URL + \
#                                              value['user__profile__avatar']
#
#         if request.user in community.subscribers.all():
#             serializer = CommunitySerializer(community)
#             return Response(
#                 {'details': serializer.data, 'active_users': json.dumps(list(active_users), cls=DjangoJSONEncoder)})
#         else:
#             return Response({"error": "not subscribed to view details."}, status=HTTP_401_UNAUTHORIZED)
#
#     except Exception as e:
#         print(e)
#         return Response({"error": "community not found"}, status=HTTP_404_NOT_FOUND)
#

@api_view(['GET'])
def get_community_details(request, cid, slug):
    try:
        now_month = timezone.now().month

        community = Community.objects.get(id=cid, slug=slug)
        active_users = Post.objects.filter(
            community=community,
            timestamp__month=now_month
        ).values(
            'user_id', 'user__username', 'user__uid',
            'user__profile__avatar',
            'user__first_name', 'user__last_name'
        ).annotate(
            Count('id', distinct=True),
            Count('likes')
        ).order_by('-id__count')[:3]

        for value in active_users:
            # value['user__profile__avatar'] = 'https://s3.us-east-2.amazonaws.com/namastenepal' +
            # settings.MEDIA_URL + value['user__profile__avatar']
            value['user__profile__avatar'] = settings.MEDIA_URL + \
                                             value['user__profile__avatar']

        if community.is_private and request.user not in community.subscribers.all():
            return Response({"error": "not subscribed to view details."}, status=HTTP_401_UNAUTHORIZED)
            # return Response({'details': serializer.data,
            # 'active_users': json.dumps(list(active_users),
            # cls=DjangoJSONEncoder)})
        else:
            serializer = CommunitySerializer(community)
            return Response({'details': serializer.data, 'active_users': active_users})

    except Exception as e:
        print(e)
        return Response({"error": "community not found"}, status=HTTP_404_NOT_FOUND)


@api_view(['GET'])
def user_community_list(request):
    if request.method == 'GET':
        community = Community.objects.filter(
            subscribers__in=[request.user]).order_by('id')
        serializer = CommunitySerializer(community, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
def pin_post(request):
    pid = request.POST.get('pid')
    if not pid:
        return Response({"error": "Invalid post id"}, status=HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(pid=pid)
        comm = Community.objects.get(id=post.community.id)
        if request.user not in comm.admin.all():
            return Response({"error": "Only admins can pin the post"},
                            status=HTTP_400_BAD_REQUEST)
    except Post.DoesNotExist:
        return Response({"error": "post not found"}, status=HTTP_400_BAD_REQUEST)

    posts = Post.objects.filter(community_id=post.community.id, pinned=True)
    for p in posts:
        p.pinned = False
        p.save()

    if post.pinned:
        post.pinned = False
        post.save()
        ctx = {'success': 'Post unpinned'}
    else:
        post.pinned = True
        post.save()
        ctx = {'success': 'Post pinned'}

    return Response(ctx, status=HTTP_200_OK)


@api_view(['POST'])
def change_icon(request):
    community = get_object_or_404(Community, id=request.data.get('samaj'))

    if not community.admin.filter(pk=request.user.pk).exists():
        return Response({"error": "Not an Admin."}, status=HTTP_400_BAD_REQUEST)
    new_pic = request.data.get('icon')
    if not new_pic:
        return Response({"error": "Icon is required."}, status=HTTP_400_BAD_REQUEST)

    _data = request.data.copy()

    serializer = IconSerializer(community, data=_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"success": "samaj icon changed successfully."}, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_background(request):
    _id = request.data.get('samaj')
    if not _id:
        return Response({"error": "Samaj is required."}, status=HTTP_400_BAD_REQUEST)

    community = Community.objects.get(id=_id)

    if not community.admin.filter(pk=request.user.pk).exists():
        return Response({"error": "Not an Admin."}, status=HTTP_400_BAD_REQUEST)

    new_pic = request.data.get('background')
    if not new_pic:
        return Response({"error": "cover pic is required."}, status=HTTP_400_BAD_REQUEST)

    _data = request.data.copy()
    serializer = BackgroundImageSerializer(community, data=_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"success": "background image change succesfully."}, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def kick_samaj_user(request):
    cid = request.data.get('id')
    uid = request.data.get('uid')
    try:
        community = Community.objects.get(id=cid)
        if request.user in community.admin.all():
            if community.subscribers.filter(uid=uid).exists:
                community.subscribers.remove(User.objects.get(uid=uid))

            serializers = CommunitySerializer(community)
            return Response({"success": "user has been kicked.", "details": serializers.data}, status=HTTP_200_OK)
        else:
            return Response({"error": "Not and admin."}, status=HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return Response({"error": "No samaj found."}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_descriptions(request):
    cid = request.data.get('id')

    descriptions = request.data.get('descriptions', None)
    if not descriptions:
        return Response({"error": "No description found."}, status=HTTP_400_BAD_REQUEST)
    try:
        community = Community.objects.get(id=cid)
    except Community.DoesNotExist:
        return Response({"error": "No samaj found."}, status=HTTP_404_NOT_FOUND)

    if request.user in community.admin.all():
        community.description = descriptions
        community.save()
        serializers = CommunitySerializer(community)
        return Response({"success": "descriptions changed successfully.", "details": serializers.data},
                        status=HTTP_200_OK)
    else:
        return Response({"error": "Not and admin."}, status=HTTP_400_BAD_REQUEST)



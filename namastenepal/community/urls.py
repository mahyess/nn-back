from django.urls import path, re_path

from .views import (
    community_list,
    pin_post,
    get_community_details,
    join_community,
    leave_community,
    request_community,
    change_icon,
    change_background,
    change_descriptions,
    kick_samaj_user,
    user_community_list,
)


urlpatterns = [
    path('', community_list, name='community-list'),

    path('my-list/', user_community_list),
    path('change-icon/', change_icon),
    path('change-background/', change_background),
    path('admin/edit/change-descriptions/', change_descriptions),
    path('admin/edit/kick-user/', kick_samaj_user),

    path('<str:cid>/<str:slug>/details/', get_community_details),

    path('post/pin/', pin_post),
    path('join/', join_community),
    path('leave/', leave_community),
    path('request/', request_community),
    # re_path(r'^(?P<slug>[\w-]+)/$', PostDetailAPIView.as_view(), name='detail'),

]

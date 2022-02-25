from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView

from namastenepal.accounts.views import (
    current_user,
    UserList,
    is_auth,
    CreateUser,
    activate,
    change_password,
    deactivate_account,
    set_fcm_token,
    PhoneVerify,
    RequestPhoneVerify,
    PhoneActivationVerify,
)
from namastenepal.core.views import (
    privacy_policy,
    storage_tech,
    terms,
    SearchAPI,
)
from namastenepal.usermodule.views import get_user_logs
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from .views import HashTagList, FrontendAppView  # , PrivateGraphQLView

urlpatterns = [
                  # re_path(r'^jet_api/', include(jet_urls)),
                  # path("jet/", include("jet_django.urls", "jet")),
                  # re_path(r"^jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
                  path("namastenepal-admin/", admin.site.urls),
                  # re_path(r"^graphql$", PrivateGraphQLView.as_view(graphiql=False)),
                  # path('offline/', offline),
                  path(
                      "api/v1/",
                      include("namastenepal.accounts.urls"),
                  ),
                  path("api/set-fcm-token/", set_fcm_token),
                  path(
                      "sw.js",
                      TemplateView.as_view(
                          template_name="sw.js", content_type="application/x-javascript"
                      ),
                  ),
                  path(
                      "firebase-messaging-sw.js",
                      TemplateView.as_view(
                          template_name="firebase-messaging-sw.js",
                          content_type="application/x-javascript",
                      ),
                  ),
                  path("about/privacy-policy/", privacy_policy, name="privacy-policy"),
                  path("about/storage-tech/", storage_tech, name="storage-tech"),
                  path("legal/terms-conditions/", terms, name="terms-conditions"),
                  path("api/register/", CreateUser.as_view()),
                  path("api/auth/phone-activation-verify/", PhoneActivationVerify.as_view()),
                  path(
                      "api/auth/phone-verify/request/<str:phone_number>/",
                      RequestPhoneVerify.as_view(),
                  ),
                  path("api/auth/phone-verify/", PhoneVerify.as_view()),
                  path("current_user/", current_user),
                  path("api/users/", UserList.as_view()),
                  path("api/is-auth/", is_auth),
                  path("api/login/", obtain_jwt_token),
                  path("api/token-refresh/", refresh_jwt_token),
                  path(
                      "api/password-reset/",
                      include("django_rest_passwordreset.urls", namespace="password-reset"),
                  ),
                  path("api/community/", include("namastenepal.community.urls")),
                  path("api/posts/", include("namastenepal.posts.urls")),
                  path("api/firebase/", include("firebase.urls")),
                  path("api/messages/", include("namastenepal.chat_messages.urls")),
                  path("api/notifications/", include("namastenepal.notifications.urls")),
                  path("api/get-user-logs/", get_user_logs),
                  path("api/user/change-password/", change_password),
                  path("api/user/account-deactivate/", deactivate_account),
                  path("api/user/", include("namastenepal.usermodule.urls")),
                  path("api/hashtags/", HashTagList.as_view()),
                  path("api/search/", SearchAPI.as_view()),
                  # path('', TemplateView.as_view(template_name='index.html'), name="base"),
                  # path('service-worker.js', TemplateView.as_view(template_name='service-worker.js',
                  #                                                content_type='application/javascript')),
                  re_path(
                      r"^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
                      activate,
                      name="activate",
                  ),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # urlpatterns += [re_path(r'^moniter/silk/',
    #                         include('silk.urls', namespace='silk'))]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r"^v1/.*", TemplateView.as_view(template_name="index.html"), name="base"),
    re_path(r"^.*", FrontendAppView.as_view()),
]

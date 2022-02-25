from django.test import SimpleTestCase
from django.urls import reverse, resolve
from ..views import PostNotificationsAPI


class TestUrls(SimpleTestCase):

    def test_all_notifications(self):
        url = reverse('all-notifications')
        self.assertEquals(resolve(url).func.view_class, PostNotificationsAPI)

    def test_all_notification(self):
        url = reverse('all-notifications')
        # print('url')
        assert 1 == 1

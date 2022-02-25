from collections import Counter
from datetime import datetime

from rest_framework.throttling import SimpleRateThrottle
from namastenepal.core.models import User


class UserLoginRateThrottle(SimpleRateThrottle):
    scope = 'loginAttempts'
    key = None
    history = []
    now: datetime = None

    def get_cache_key(self, request, view):
        user = User.objects.filter(username=request.data.get('username'))
        ident = user[0].pk if user else self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()

            # uncomment this on prod
            # ------------------
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()

        if len(self.history) >= 3:
            data = Counter(self.history)
            for key, value in data.items():
                if value == 3:
                    return self.throttle_failure()

        # ---------------------------
        # throttle_success
        user = User.objects.filter(username=request.data.get('username'))
        if user:
            self.history.insert(0, user[0].id)

        return self.throttle_success()

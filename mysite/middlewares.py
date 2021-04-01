from datetime import timedelta

from django.contrib import auth
from django.contrib.messages.storage import session
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.deprecation import MiddlewareMixin
# import datetime

from django.contrib.auth import logout
from django.utils.timezone import utc

from Cinema.settings import LOGOUT_TIME


# from django.contrib.sessions.backends.db import SessionStore


class AutoLogout(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:

            active = request.session.get('last_action')
            if active:
                last = datetime.strptime(active, "%Y-%m-%d %H:%M:%S.%f%z")

                if datetime.now(utc) - last > LOGOUT_TIME:
                    logout(request)
                else:
                    request.session['last_action'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f%z")
            else:
                request.session['last_action'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f%z")

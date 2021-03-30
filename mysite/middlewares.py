from datetime import timedelta

from django.contrib import auth
from django.contrib.messages.storage import session
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.deprecation import MiddlewareMixin
# import datetime

from django.contrib.auth import logout
from Cinema.settings import LOGOUT_TIME


# from django.contrib.sessions.backends.db import SessionStore


class AutoLogout(MiddlewareMixin):
    # s = SessionStore()
    # session
    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            # request.session['last_action'] = datetime.datetime.now()
            # request.session.get('last_action') = datetime.datetime.now()
            # last_active = str(request.session['last_touch'])
            # last_active = request.session['last_touch']
            # last_active = str(request.session.get('time'))
            # naive = last_active.replace(tzinfo=None)
            request.session['last_action'] = str(timezone.now())
            last_active = request.session['last_action']
            print(last_active, 'LAST')
            if last_active is not None:
                last_active = datetime.strptime(last_active, "%Y-%m-%d %H:%M:%S.%f%z")
                print(last_active, "LAST111")
                if timezone.now() - last_active > LOGOUT_TIME:
                    print(last_active, "LAST2222")
                    logout(request)
                else:
                    request.session['last_action'] = str(timezone.now())
                    print(last_active, "LAST33333")
            else:
                request.session['last_action'] = str(timezone.now())
                print(last_active, "LAST444")
        #     try:
        #         last_active = request.session['last_action']
        #         last_active = datetime.strptime(last_active, "%Y-%m-%d %H:%M:%S.%f%z")
        #         if datetime.now() - last_active > LOGOUT_TIME:
        #             auth.logout(request)
        #             del request.session['last_action']
        #             return
        #     except KeyError:
        #         pass
        # else:
        #     request.session['last_action'] = timezone.now()

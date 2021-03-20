# from django.utils.deprecation import MiddlewareMixin
# from datetime import datetime, timedelta
# from django.contrib import auth
#
#
# class AutoLogout(MiddlewareMixin):
#     def process_request(self, request):
#         if not request.user.is_authenticated:
#             return
#
#         try:
#             if datetime.now() - request.session['last_active'] > timedelta(seconds=0.5 * 10):
#                 auth.logout(request)
#                 del request.session['last_active']
#                 return
#         except KeyError:
#             pass

from django.contrib import admin
from django.urls import include, path, re_path

# from mysite.views import
from mysite.views import UserLoginView, RegistrationView, UserLogout, SeanceCreatView, HallCreatView, SeanceListView, \
    SeanceUpdateView, SeanceTodayListView, SeanceTomorrowListView, BuyingCreateView, OrdersListView

urlpatterns = [
    path('', SeanceListView.as_view()),
    path('buying/', BuyingCreateView.as_view(), name='buying'),
    path('orders/', OrdersListView.as_view(), name='orders'),
    path('create_hall/', HallCreatView.as_view(), name='create_hall'),
    path('create_seance/', SeanceCreatView.as_view(), name='create_seance'),
    # path('update_hall/<int:pk>/', HallUpdateView.as_view(), name='update_hall'),
    path('update_seance/<int:pk>/', SeanceUpdateView.as_view(), name='update_seance'),
    path('today', SeanceTodayListView.as_view(), name='today'),
    path('tomorrow', SeanceTomorrowListView.as_view(), name='tomorrow'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('admin/', admin.site.urls)
]

from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework.authtoken import views
from mysite.api.resourse import SeanceViewSet, OrderViewSet, HallViewSet, AuthViewSet, AuthToken
from mysite.views import UserLoginView, RegistrationView, UserLogout, SeanceCreatView, HallCreatView, SeanceListView, \
    SeanceUpdateView, SeanceTomorrowListView, BuyingCreateView, OrdersListView

router = routers.SimpleRouter()
router.register(r'seance', SeanceViewSet, basename="seance")
router.register(r'order', OrderViewSet)
router.register(r'hall', HallViewSet)
router.register(r'auth', AuthViewSet, basename='auth')


urlpatterns = [
    path('cinema/', SeanceListView.as_view()),
    path('api/', include(router.urls)),
    path('buying/', BuyingCreateView.as_view(), name='buying'),
    path('orders/', OrdersListView.as_view(), name='orders'),
    path('create_hall/', HallCreatView.as_view(), name='create_hall'),
    path('create_seance/', SeanceCreatView.as_view(), name='create_seance'),
    # path('update_hall/<int:pk>/', HallUpdateView.as_view(), name='update_hall'),
    path('update_seance/<int:pk>/', SeanceUpdateView.as_view(), name='update_seance'),
    path('tomorrow', SeanceTomorrowListView.as_view(), name='tomorrow'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('admin/', admin.site.urls)
]
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', AuthToken.as_view())
]
